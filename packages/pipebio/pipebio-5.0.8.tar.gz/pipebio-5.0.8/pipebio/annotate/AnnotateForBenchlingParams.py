from enum import Enum
from typing import List, Dict, Union, Any, Set, Optional
from dataclasses import dataclass
from typing import Literal

from pipebio.annotate.params import FilterableSelectableParams, safely_get
from pipebio.shared_python.selection_range import SelectionRange
from pipebio.shared_python.exceptions import UserFacingException


# Example enum
class DomainType(Enum):
    GermlineBased = 'GermlineBased'
    Constant = 'Constant'
    Linker = 'Linker'


@dataclass(frozen=True)
class DomainBase:
    name: str


@dataclass(frozen=True)
class ConstantDomain(DomainBase):
    reference_sequences: List[str]
    type: Literal[DomainType.Constant] = DomainType.Constant

    def __post_init__(self):
        if not self.reference_sequences or len(self.reference_sequences) == 0:
            raise UserFacingException(f'Domain "{self.name}" must have reference_sequences specified.')


@dataclass(frozen=True)
class GermlineBasedDomain(DomainBase):
    germline_ids: List[str]
    type: Literal[DomainType.GermlineBased] = DomainType.GermlineBased

    def __post_init__(self):
        if not self.germline_ids or len(self.germline_ids) == 0:
            raise UserFacingException(f'Domain "{self.name}" requires at least one germline_id.')


@dataclass(frozen=True)
class LinkerDomain(DomainBase):
    reference_sequences: List[str] = None
    type: Literal[DomainType.Linker] = DomainType.Linker

    def __post_init__(self):
        if self.reference_sequences is None:
            object.__setattr__(self, 'reference_sequences', [
                "GGCGGCGGCGGCTCC",
                "GGCGGCGGCGGCTCCGGCGGCGGCGGCTCC",
                "GGCGGCGGCGGCTCCGGCGGCGGCGGCTCCGGCGGCGGCGGCTCC"
            ])


Domain = Union[ConstantDomain, GermlineBasedDomain, LinkerDomain]


def parse_domain(domain_data: Union[Dict, Domain]) -> Domain:
    """Convert a dict to the appropriate Domain dataclass based on its type field."""
    if not isinstance(domain_data, dict):
        return domain_data

    domain_type = safely_get(domain_data, 'type', None)

    # Handle both enum and string values.
    if domain_type == DomainType.Constant or domain_type == DomainType.Constant.value:
        return ConstantDomain(**domain_data)
    elif domain_type == DomainType.GermlineBased or domain_type == DomainType.GermlineBased.value:
        return GermlineBasedDomain(**domain_data)
    elif domain_type == DomainType.Linker or domain_type == DomainType.Linker.value:
        return LinkerDomain(**domain_data)
    else:
        raise ValueError(f"Unknown domain type: {domain_type}")


def domain_to_dict(domain: Domain) -> Dict[str, Any]:
    """Convert a Domain dataclass to a dict for JSON serialization."""
    result: Dict[str, Any] = {
        'name': domain.name,
        'type': domain.type.value if isinstance(domain.type, DomainType) else domain.type
    }

    if isinstance(domain, ConstantDomain):
        result['reference_sequences'] = domain.reference_sequences
    elif isinstance(domain, GermlineBasedDomain):
        result['germline_ids'] = domain.germline_ids
    elif isinstance(domain, LinkerDomain):
        result['reference_sequences'] = domain.reference_sequences

    return result


class ShortScaffold(FilterableSelectableParams):
    domains: List[Domain]
    ALLOWED_KEYS: Set[str] = {
        'domains', 'filter', 'selection', 'sort',
        'targetFolderId', 'targetProjectId', 'workflowId', 'outputNames', 'inputs'
    }
    MAX_DOMAINS: int = 100

    def __init__(self,
                 domains: Optional[List[Domain]] = None,
                 selection: Optional[Union[List[SelectionRange], SelectionRange]] = None,
                 filter: Optional[str] = None,
                 params: Optional[Dict] = None):
        if params:
            self._validate_unknown_keys(params)
            super().__init__(params)
            domains_data = safely_get(params, "domains", [])
            if not domains_data:
                raise UserFacingException('Scaffold must contain at least one domain.')
            if len(domains_data) > self.MAX_DOMAINS:
                raise UserFacingException(
                    f'Scaffold contains {len(domains_data)} domains, which exceeds the maximum allowed ({self.MAX_DOMAINS}). '
                    f'Please reduce the number of domains.'
                )
            self.domains = [parse_domain(domain) for domain in domains_data]
            self._validate_no_adjacent_variable_domains()
        else:
            super().__init__({})
            if not domains:
                raise UserFacingException('Scaffold must contain at least one domain.')
            if len(domains) > self.MAX_DOMAINS:
                raise UserFacingException(
                    f'Scaffold contains {len(domains)} domains, which exceeds the maximum allowed ({self.MAX_DOMAINS}). '
                    f'Please reduce the number of domains.'
                )
            self.domains = domains
            self._validate_no_adjacent_variable_domains()

            if selection:
                if isinstance(selection, SelectionRange):
                    self.selection = [selection]
                else:
                    self.selection = selection

            if filter:
                self.filter = filter

    def _validate_unknown_keys(self, params: Dict):
        unknown_keys = set(params.keys()) - self.ALLOWED_KEYS
        if unknown_keys:
            raise UserFacingException(
                f'Unknown parameter keys in scaffold: {", ".join(sorted(unknown_keys))}. '
                f'Allowed keys are: {", ".join(sorted(self.ALLOWED_KEYS))}'
            )

    def _validate_no_adjacent_variable_domains(self):
        """Validate that there are no adjacent GermlineBasedDomain (variable) domains.
        Currently, we have only test coverage for scaffolds with non-consecutive variable domains,
        but we may turn off this validation in the future if we need to support it."""

        for i in range(len(self.domains) - 1):
            current_domain = self.domains[i]
            next_domain = self.domains[i + 1]

            # Check if both consecutive domains are GermlineBasedDomain (variable domains)
            if isinstance(current_domain, GermlineBasedDomain) and isinstance(next_domain, GermlineBasedDomain):
                raise ValueError(
                    f"Adjacent variable domains found at positions {i} and {i + 1}: "
                    f"'{current_domain.name}' and '{next_domain.name}'. "
                    f"Variable domains (GermlineBased) must be separated by Constant or Linker domains."
                )

    def to_json(self):
        also = super().to_json()

        return {
            **also,
            'domains': [domain_to_dict(domain) for domain in self.domains],
        }


class AnnotateForBenchlingParams:
    target_folder_id: str
    scaffolds: List[ShortScaffold]

    def __init__(self,
                 target_folder_id: Optional[str] = None,
                 scaffolds: Optional[List[ShortScaffold]] = None,
                 germline_ids: Optional[List[str]] = None,
                 translation_table: Optional[str] = None,
                 params: Optional[Dict] = None):
        if params:
            scaffolds_data = safely_get(params, 'scaffolds', [])
            if not scaffolds_data:
                raise UserFacingException('At least one scaffold must be provided.')
            self.scaffolds = [ShortScaffold(params=scaffold) for scaffold in scaffolds_data]
            self.target_folder_id = safely_get(params, "targetFolderId", None)
            if not self.target_folder_id:
                raise UserFacingException('target_folder_id is required.')
            self._translation_table = safely_get(params, "translationTable", "Standard")
            if "germlineId" in params:
                self.germline_ids = [safely_get(params, "germlineId", None)]
            else:
                self.germline_ids = safely_get(params, "germlineIds", [])
        else:
            if not target_folder_id:
                raise UserFacingException('target_folder_id is required.')
            self.target_folder_id = target_folder_id
            if not scaffolds:
                raise UserFacingException('At least one scaffold must be provided.')
            self.scaffolds = scaffolds if scaffolds else []
            self.germline_ids = germline_ids if germline_ids else []
            self._translation_table = translation_table if translation_table else "Standard"

    def to_json(self):
        return {
            'scaffolds': [scaffold.to_json() for scaffold in self.scaffolds],
            'targetFolderId': self.target_folder_id,
            'germlineIds': self.germline_ids,
            'translationTable': self._translation_table
        }
