"""
Módulo de Tipos de Projeto para o HighBond SDK.
"""
from typing import Optional, Dict, Any, List, Generator

from ..http_client import HighBondHTTPClient, PaginationMixin, ThreadingMixin
from ..config import PaginationConfig, ThreadingConfig
from ..utils import to_dataframe


class ProjectTypesModule(PaginationMixin, ThreadingMixin):
    """Módulo para gerenciamento de Tipos de Projeto no HighBond.
    
    Tipos de projeto definem categorias e configurações padrão para projetos.
    """
    
    def __init__(
        self,
        http_client: HighBondHTTPClient,
        org_id: int,
        pagination_config: PaginationConfig,
        threading_config: ThreadingConfig
    ):
        """
        Args:
            http_client: Cliente HTTP configurado.
            org_id: ID da organização.
            pagination_config: Configuração de paginação.
            threading_config: Configuração de threading.
        """
        self._http_client = http_client
        self._org_id = org_id
        self._pagination_config = pagination_config
        self._threading_config = threading_config
    
    @property
    def _base_endpoint(self) -> str:
        """Endpoint base para tipos de projeto."""
        return f"/orgs/{self._org_id}/project_types"
    
    def list_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
        return_pandas: bool = False
    ) -> List[Dict[str, Any]]:
        """Lista todos os tipos de projeto com paginação automática.
        
        Args:
            filters: Filtros adicionais.
            max_pages: Máximo de páginas a buscar (None = todas).
            return_pandas: Se True, retorna um DataFrame; se False, retorna uma lista.
            
        Returns:
            Lista de tipos de projeto ou DataFrame.
            
        Example:
            >>> for pt in client.project_types.list_all():
            ...     print(pt['attributes']['name'])
        """
        pagination = PaginationConfig(
            page_size=self._pagination_config.page_size,
            max_pages=max_pages or self._pagination_config.max_pages
        )
        
        params = {}
        if filters:
            for key, value in filters.items():
                params[f"filter[{key}]"] = value
        
        project_types = list(self._paginate(self._base_endpoint, pagination, params))
        
        if return_pandas:
            return to_dataframe(project_types)
        return project_types
    
    def get(self, project_type_id: int, return_pandas: bool = False) -> Dict[str, Any]:
        """Obtém um tipo de projeto específico por ID.
        
        Args:
            project_type_id: ID do tipo de projeto.
            return_pandas: Se True, retorna um DataFrame; se False, retorna resposta da API.
            
        Returns:
            Dados do tipo de projeto ou DataFrame.
            
        Example:
            >>> pt = client.project_types.get(123)
            >>> print(pt['data']['attributes']['name'])
        """
        endpoint = f"{self._base_endpoint}/{project_type_id}"
        response = self._http_client.get(endpoint, None)
        
        if return_pandas:
            return to_dataframe(response)
        return response
    
    def get_many(
        self,
        project_type_ids: List[int],
        return_pandas: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtém múltiplos tipos de projeto em paralelo.
        
        Args:
            project_type_ids: Lista de IDs de tipos de projeto.
            return_pandas: Se True, retorna um DataFrame; se False, retorna lista.
            
        Returns:
            Lista de dados de tipos de projeto ou DataFrame.
            
        Example:
            >>> types = client.project_types.get_many([1, 2, 3])
            >>> for pt in types:
            ...     print(pt['data']['attributes']['name'])
        """
        def fetch_type(pid):
            return self.get(pid, return_pandas=False)
        
        project_types = self._execute_parallel(
            fetch_type,
            project_type_ids,
            self._threading_config
        )
        
        if return_pandas:
            return to_dataframe(project_types)
        return project_types
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        certification: Optional[bool] = None,
        control_performance: Optional[bool] = None,
        risk_assurance: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Cria um novo tipo de projeto.
        
        Args:
            name: Nome do tipo de projeto (obrigatório).
            description: Descrição do tipo de projeto.
            certification: Habilitar certificações (requer System Admin + Professional).
            control_performance: Habilitar control performance.
            risk_assurance: Habilitar risk assurance.
            
        Returns:
            Dados do tipo de projeto criado.
            
        Example:
            >>> pt = client.project_types.create(
            ...     name="Auditoria Interna",
            ...     description="Tipo para auditorias internas",
            ...     certification=True
            ... )
        """
        attributes = {"name": name}
        
        optional_attrs = {
            "description": description,
            "certification": certification,
            "control_performance": control_performance,
            "risk_assurance": risk_assurance
        }
        
        for key, value in optional_attrs.items():
            if value is not None:
                attributes[key] = value
        
        payload = {
            "data": {
                "type": "project_types",
                "attributes": attributes
            }
        }
        
        return self._http_client.post(self._base_endpoint, payload)
    
    def update(
        self,
        project_type_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        certification: Optional[bool] = None,
        control_performance: Optional[bool] = None,
        risk_assurance: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Atualiza um tipo de projeto existente.
        
        Args:
            project_type_id: ID do tipo de projeto a atualizar.
            name: Novo nome.
            description: Nova descrição.
            certification: Habilitar/desabilitar certificações.
            control_performance: Habilitar/desabilitar control performance.
            risk_assurance: Habilitar/desabilitar risk assurance.
            
        Returns:
            Dados do tipo de projeto atualizado.
            
        Example:
            >>> pt = client.project_types.update(
            ...     project_type_id=123,
            ...     name="Auditoria Externa"
            ... )
        """
        attributes = {}
        
        optional_attrs = {
            "name": name,
            "description": description,
            "certification": certification,
            "control_performance": control_performance,
            "risk_assurance": risk_assurance
        }
        
        for key, value in optional_attrs.items():
            if value is not None:
                attributes[key] = value
        
        payload = {
            "data": {
                "type": "project_types",
                "id": str(project_type_id),
                "attributes": attributes
            }
        }
        
        endpoint = f"{self._base_endpoint}/{project_type_id}"
        return self._http_client.patch(endpoint, payload)
    
    def delete(self, project_type_id: int) -> Dict[str, Any]:
        """Exclui um tipo de projeto.
        
        Args:
            project_type_id: ID do tipo de projeto a excluir.
            
        Returns:
            Resposta da API (geralmente vazia em sucesso).
            
        Warning:
            Esta ação é irreversível e pode afetar projetos existentes.
            
        Example:
            >>> client.project_types.delete(123)
        """
        endpoint = f"{self._base_endpoint}/{project_type_id}"
        return self._http_client.delete(endpoint)
    
    def delete_many(self, project_type_ids: List[int]) -> List[Dict[str, Any]]:
        """Exclui múltiplos tipos de projeto em paralelo.
        
        Args:
            project_type_ids: Lista de IDs de tipos de projeto a excluir.
            
        Returns:
            Lista de respostas da API.
            
        Warning:
            Esta ação é irreversível!
        """
        return self._execute_parallel(
            self.delete,
            project_type_ids,
            self._threading_config
        )
