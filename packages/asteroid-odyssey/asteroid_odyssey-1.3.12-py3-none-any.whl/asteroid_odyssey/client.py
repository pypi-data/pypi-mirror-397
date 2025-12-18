"""
Asteroid Agents Python SDK - High-Level Client Interface

Provides a clean, easy-to-use interface for interacting with the Asteroid Agents API,
similar to the TypeScript SDK.

This module provides a high-level client that wraps the generated OpenAPI client
without modifying any generated files.
"""

import time
import os
import base64
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple, NamedTuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from .agents_v1_gen import (
    Configuration as AgentsV1Configuration,
    ApiClient as AgentsV1ApiClient,
    AgentProfileApi as AgentsV1AgentProfileApi,
    CreateAgentProfileRequest,
    UpdateAgentProfileRequest,
    DeleteAgentProfile200Response,
    AgentProfile,
    Credential,
)
from .agents_v1_gen.exceptions import ApiException
from .agents_v2_gen import (
    AgentsAgentBase as Agent,
    AgentList200Response as AgentList200Response,
    Configuration as AgentsV2Configuration,
    ApiClient as AgentsV2ApiClient,
    AgentsApi as AgentsV2AgentsApi,
    ExecutionApi as AgentsV2ExecutionApi,
    FilesApi as AgentsV2FilesApi,
    AgentsExecutionActivity as ExecutionActivity,
    AgentsExecutionUserMessagesAddTextBody as ExecutionUserMessagesAddTextBody,
    AgentsFilesFile as File,
    AgentsAgentExecuteAgentRequest as ExecuteAgentRequest,
    AgentsFilesTempFile as TempFile,
    AgentsFilesTempFilesResponse as TempFilesResponse,
    AgentsExecutionSortField as ExecutionSortField,
    AgentsExecutionStatus as ExecutionStatus,
    AgentsExecutionListItem as ExecutionListItem,
    AgentsExecutionExecutionResult as ExecutionResult,
    ExecutionsList200Response,
    CommonSortDirection as SortDirection,
)


class AsteroidAPIError(Exception):
    """Base exception for all Asteroid API related errors."""
    pass


class ExecutionError(AsteroidAPIError):
    """Raised when an execution fails or is cancelled."""
    def __init__(self, message: str, execution_result: Optional[ExecutionResult] = None):
        super().__init__(message)
        self.execution_result = execution_result


class TimeoutError(AsteroidAPIError):
    """Raised when an execution times out."""
    def __init__(self, message: str):
        super().__init__(message)


class AgentInteractionResult(NamedTuple):
    """Result returned by wait_for_agent_interaction method."""
    is_terminal: bool  # True if execution reached a terminal state
    status: str  # Current execution status
    agent_message: Optional[str]  # Agent's message if requesting interaction
    execution_result: Optional[ExecutionResult]  # Final result if terminal


def encrypt_with_public_key(plaintext: str, pem_public_key: str) -> str:
    """
    Encrypt plaintext using RSA public key with PKCS1v15 padding.

    Args:
        plaintext: The string to encrypt
        pem_public_key: PEM-formatted RSA public key

    Returns:
        Base64-encoded encrypted string

    Raises:
        ValueError: If encryption fails or key is invalid

    Example:
        encrypted = encrypt_with_public_key("my_password", public_key_pem)
    """
    try:
        # Load the PEM public key (matches node-forge behavior)
        public_key = serialization.load_pem_public_key(pem_public_key.encode('utf-8'))

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Invalid RSA public key")

        # Encrypt using PKCS1v15 padding (matches "RSAES-PKCS1-V1_5" from TypeScript)
        encrypted_bytes = public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.PKCS1v15()
        )

        # Encode as base64 (matches forge.util.encode64)
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    except Exception as e:
        raise ValueError(f"Failed to encrypt: {str(e)}") from e


class AsteroidClient:
    """
    High-level client for the Asteroid Agents API.

    This class provides a convenient interface for executing agents and managing
    their execution lifecycle, similar to the TypeScript SDK.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Create an API client with the provided API key.

        Args:
            api_key: Your API key for authentication
            base_url: Optional base URL (defaults to https://odyssey.asteroid.ai)

        Example:
            client = AsteroidClient('your-api-key')
        """
        if api_key is None:
            raise TypeError("API key cannot be None")

        base = base_url or "https://odyssey.asteroid.ai"

        # Configure the V1 API client (used for agent profiles and credentials)
        v1_config = AgentsV1Configuration(
            host=f"{base}/api/v1",
            api_key={'ApiKeyAuth': api_key}
        )
        self.api_client = AgentsV1ApiClient(v1_config)
        self.agent_profile_api = AgentsV1AgentProfileApi(self.api_client)

        # Configure the V2 API client (used for agents, executions, files)
        v2_config = AgentsV2Configuration(
            host=f"{base}/agents/v2",
            api_key={'ApiKeyAuth': api_key}
        )
        self.agents_v2_api_client = AgentsV2ApiClient(v2_config)
        self.agents_v2_agents_api = AgentsV2AgentsApi(self.agents_v2_api_client)
        self.agents_v2_execution_api = AgentsV2ExecutionApi(self.agents_v2_api_client)
        self.agents_v2_files_api = AgentsV2FilesApi(self.agents_v2_api_client)

    # --- V2 ---

    def execute_agent(
        self,
        agent_id: str,
        dynamic_data: Optional[Dict[str, Any]] = None,
        agent_profile_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        temp_files: Optional[List[TempFile]] = None,
        version: Optional[int] = None,
    ) -> str:
        """
        Execute an agent with the provided parameters.

        Args:
            agent_id: The ID of the agent to execute
            dynamic_data: Dynamic data to be merged into the placeholders defined in prompts
            agent_profile_id: Optional ID of the agent profile to use
            metadata: Optional metadata key-value pairs for organizing and filtering executions
            temp_files: Optional list of temporary files to attach (must be pre-uploaded using stage_temp_files)
            version: Optional version of the agent to execute. If not provided, the latest version will be used.

        Returns:
            The execution ID

        Raises:
            AsteroidAPIError: If the execution request fails

        Example:
            execution_id = client.execute_agent('my-agent-id', {'input': 'some dynamic value'})
            execution_id = client.execute_agent('my-agent-id', {'input': 'value'}, version=3)
        """
        req = ExecuteAgentRequest(
            dynamic_data=dynamic_data,
            agent_profile_id=agent_profile_id,
            metadata=metadata,
            temp_files=temp_files,
            version=version,
        )
        try:
            response = self.agents_v2_agents_api.agent_execute_post(agent_id, req)
            return response.execution_id
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to execute agent: {e}") from e

    def get_execution(self, execution_id: str) -> ExecutionListItem:
        """
        Get a single execution by ID with all details.

        This method returns comprehensive execution information including status,
        result, browser recording URL, and other metadata.

        Args:
            execution_id: The execution identifier

        Returns:
            The execution details including:
            - status: Current execution status
            - execution_result: Result with outcome and reasoning (if terminal)
            - browser_recording_url: Recording URL (if browser session was used)
            - browser_live_view_url: Live view URL (if execution is running)
            - agent_id, agent_name, agent_version: Agent information
            - created_at, terminal_at, duration: Timing information
            - metadata, comments, human_labels: Additional data

        Raises:
            AsteroidAPIError: If the request fails

        Example:
            execution = client.get_execution(execution_id)
            print(f"Status: {execution.status}")
            if execution.execution_result:
                print(f"Outcome: {execution.execution_result.outcome}")
            if execution.browser_recording_url:
                print(f"Recording: {execution.browser_recording_url}")
        """
        try:
            return self.agents_v2_execution_api.execution_get(execution_id)
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get execution: {e}") from e

    def wait_for_execution_result(
        self,
        execution_id: str,
        interval: float = 1.0,
        timeout: float = 3600.0
    ) -> ExecutionResult:
        """
        Wait for an execution to reach a terminal state and return the result.

        Continuously polls the execution until it's either "completed",
        "cancelled", or "failed".

        Args:
            execution_id: The execution identifier
            interval: Polling interval in seconds (default is 1.0)
            timeout: Maximum wait time in seconds (default is 3600 - 1 hour)

        Returns:
            The execution result object

        Raises:
            ValueError: If interval or timeout parameters are invalid
            TimeoutError: If the execution times out
            ExecutionError: If the execution ends as "cancelled" or "failed"

        Example:
            result = client.wait_for_execution_result(execution_id, interval=2.0)
            print(result.outcome, result.reasoning)
        """
        # Validate input parameters
        if interval <= 0:
            raise ValueError("interval must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise TimeoutError(f"Execution {execution_id} timed out after {timeout}s")

            execution = self.get_execution(execution_id)
            current_status = execution.status

            if current_status == ExecutionStatus.COMPLETED:
                if execution.execution_result:
                    return execution.execution_result
                # Execution completed but result not ready yet, wait a bit more
                time.sleep(interval)
                continue

            elif current_status in [ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                raise ExecutionError(
                    f"Execution {execution_id} ended with status: {current_status.value}",
                    execution.execution_result
                )

            # Wait for the specified interval before polling again
            time.sleep(interval)

    def upload_execution_files(
        self,
        execution_id: str,
        files: List[Union[bytes, str, Tuple[str, bytes]]],
        default_filename: str = "file.txt"
    ) -> str:
        """
        Upload files to a running execution.

        Use this method to upload files to an execution that is already in progress.
        If you want to attach files to an execution before it starts, use stage_temp_files instead.

        Args:
            execution_id: The execution identifier
            files: List of files to upload. Each file can be:
                   - bytes: Raw file content (will use default_filename)
                   - str: File path as string (will read file and use filename)
                   - Tuple[str, bytes]: (filename, file_content) tuple
            default_filename: Default filename to use when file is provided as bytes

        Returns:
            Success message from the API

        Raises:
            AsteroidAPIError: If the upload request fails

        Example:
            # Upload with file content
            with open('hello.txt', 'r') as f:
                file_content = f.read()

            response = client.upload_execution_files(execution_id, [file_content.encode()])

            # Upload with filename and content
            files = [('hello.txt', file_content.encode())]
            response = client.upload_execution_files(execution_id, files)

            # Or create content directly
            hello_content = "Hello World!".encode()
            response = client.upload_execution_files(execution_id, [hello_content])
        """
        try:
            # Process files to ensure proper format for the V2 API
            processed_files = []
            for file_item in files:
                if isinstance(file_item, tuple):
                    # Already in (filename, content) format
                    filename, content = file_item
                    if isinstance(content, str):
                        content = content.encode()
                    processed_files.append((filename, content))
                elif isinstance(file_item, str):
                    # Check if string is a file path that exists, otherwise treat as content
                    if os.path.isfile(file_item):
                        # File path - read the file
                        filename = os.path.basename(file_item)
                        with open(file_item, 'rb') as f:
                            content = f.read()
                        processed_files.append((filename, content))
                    else:
                        # String content - encode and use default filename
                        content = file_item.encode()
                        processed_files.append((default_filename, content))
                elif isinstance(file_item, bytes):
                    # Raw bytes - use default filename
                    processed_files.append((default_filename, file_item))
                else:
                    # Other types - convert to string content and encode
                    content = str(file_item).encode()
                    processed_files.append((default_filename, content))

            response = self.agents_v2_files_api.execution_context_files_upload(execution_id, files=processed_files)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to upload execution files: {e}") from e

    # --- V1 (Agent Profiles) ---

    def get_agent_profiles(self, organization_id: str) -> List[AgentProfile]:
        """
        Get a list of agent profiles for a specific organization.

        Args:
            organization_id: The organization identifier (required)
        Returns:
            A list of agent profiles
        Raises:
            Exception: If the agent profiles request fails
        Example:
            profiles = client.get_agent_profiles("org-123")
        """
        try:
            response = self.agent_profile_api.get_agent_profiles(organization_id=organization_id)
            return response  # response is already a List[AgentProfile]
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get agent profiles: {e}") from e
    def get_agent_profile(self, profile_id: str) -> AgentProfile:
        """
        Get an agent profile by ID.
        Args:
            profile_id: The ID of the agent profile
        Returns:
            The agent profile
        Raises:
            Exception: If the agent profile request fails
        Example:
            profile = client.get_agent_profile("profile_id")
        """
        try:
            response = self.agent_profile_api.get_agent_profile(profile_id)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get agent profile: {e}") from e

    def create_agent_profile(self, request: CreateAgentProfileRequest) -> AgentProfile:
        """
        Create an agent profile with automatic credential encryption.

        Args:
            request: The request object
        Returns:
            The agent profile
        Raises:
            Exception: If the agent profile creation fails
        Example:
            request = CreateAgentProfileRequest(
                name="My Agent Profile",
                description="This is my agent profile",
                organization_id="org-123",
                proxy_cc=CountryCode.US,
                proxy_type=ProxyType.RESIDENTIAL,
                captcha_solver_active=True,
                sticky_ip=True,
                credentials=[Credential(name="user", data="password")]
            )
            profile = client.create_agent_profile(request)
        """
        try:
            # Create a copy to avoid modifying the original request
            processed_request = request

            # If credentials are provided, encrypt them before sending
            if request.credentials and len(request.credentials) > 0:
                # Get the public key for encryption
                public_key = self.get_credentials_public_key()

                # Encrypt each credential's data field
                encrypted_credentials = []
                for credential in request.credentials:
                    encrypted_credential = Credential(
                        name=credential.name,
                        data=encrypt_with_public_key(credential.data, public_key),
                        id=credential.id,
                        created_at=credential.created_at
                    )
                    encrypted_credentials.append(encrypted_credential)

                # Create new request with encrypted credentials
                processed_request = CreateAgentProfileRequest(
                    name=request.name,
                    description=request.description,
                    organization_id=request.organization_id,
                    proxy_cc=request.proxy_cc,
                    proxy_type=request.proxy_type,
                    captcha_solver_active=request.captcha_solver_active,
                    sticky_ip=request.sticky_ip,
                    credentials=encrypted_credentials
                )

            response = self.agent_profile_api.create_agent_profile(processed_request)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to create agent profile: {e}") from e
    def update_agent_profile(self, profile_id: str, request: UpdateAgentProfileRequest) -> AgentProfile:
        """
        Update an agent profile with automatic credential encryption.

        Args:
            profile_id: The ID of the agent profile
            request: The request object
        Returns:
            The agent profile
        Raises:
            Exception: If the agent profile update fails
        Example:
            request = UpdateAgentProfileRequest(
                name="My Agent Profile",
                description="This is my agent profile",
                credentials_to_add=[Credential(name="api_key", data="secret")]
            )
            profile = client.update_agent_profile("profile_id", request)
        """
        try:
            # Create a copy to avoid modifying the original request
            processed_request = request

            # If credentials_to_add are provided, encrypt them before sending
            if request.credentials_to_add and len(request.credentials_to_add) > 0:
                # Get the public key for encryption
                public_key = self.get_credentials_public_key()

                # Encrypt the data field of each credential to add
                encrypted_credentials_to_add = []
                for credential in request.credentials_to_add:
                    encrypted_credential = Credential(
                        name=credential.name,
                        data=encrypt_with_public_key(credential.data, public_key),
                        id=credential.id,
                        created_at=credential.created_at
                    )
                    encrypted_credentials_to_add.append(encrypted_credential)

                # Create new request with encrypted credentials
                processed_request = UpdateAgentProfileRequest(
                    name=request.name,
                    description=request.description,
                    proxy_cc=request.proxy_cc,
                    proxy_type=request.proxy_type,
                    captcha_solver_active=request.captcha_solver_active,
                    sticky_ip=request.sticky_ip,
                    credentials_to_add=encrypted_credentials_to_add,
                    credentials_to_delete=request.credentials_to_delete
                )

            response = self.agent_profile_api.update_agent_profile(profile_id, processed_request)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to update agent profile: {e}") from e
    def delete_agent_profile(self, profile_id: str) -> DeleteAgentProfile200Response:
        """
        Delete an agent profile.
        Args:
            profile_id: The ID of the agent profile
        Returns:
            Confirmation message from the server
        Raises:
            Exception: If the agent profile deletion fails
        Example:
            response = client.delete_agent_profile("profile_id")
        """
        try:
            response = self.agent_profile_api.delete_agent_profile(profile_id)
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to delete agent profile: {e}") from e

    def get_credentials_public_key(self) -> str:
        """
        Get the public key for encrypting credentials.

        Returns:
            PEM-formatted RSA public key string

        Raises:
            Exception: If the public key request fails

        Example:
            public_key = client.get_credentials_public_key()
        """
        try:
            response = self.agent_profile_api.get_credentials_public_key()
            return response
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get credentials public key: {e}") from e

    def wait_for_agent_interaction(
        self,
        execution_id: str,
        poll_interval: float = 2.0,
        timeout: float = 3600.0
    ) -> AgentInteractionResult:
        """
        Wait for an agent interaction request or terminal state.

        This method polls an existing execution until it either:
        1. Requests human input (paused_by_agent state)
        2. Reaches a terminal state (completed, failed, cancelled)
        3. Times out

        Unlike interactive_agent, this method doesn't start an execution or handle
        the response automatically - it just waits and reports what happened.

        Args:
            execution_id: The execution identifier for an already started execution
            poll_interval: How often to check for updates in seconds (default: 2.0)
            timeout: Maximum wait time in seconds (default: 3600 - 1 hour)

        Returns:
            AgentInteractionResult containing:
            - is_terminal: True if execution finished (completed/failed/cancelled)
            - status: Current execution status string
            - agent_message: Agent's message if requesting interaction (None if terminal)
            - execution_result: Final result if terminal state (None if requesting interaction)

        Raises:
            ValueError: If interval or timeout parameters are invalid
            TimeoutError: If the execution times out
            AsteroidAPIError: If API calls fail

        Example:
            # Start an execution first
            execution_id = client.execute_agent('agent-id', {'input': 'test'})

            # Wait for interaction or completion
            result = client.wait_for_agent_interaction(execution_id)

            if result.is_terminal:
                print(f"Execution finished with status: {result.status}")
                if result.execution_result:
                    print(f"Result: {result.execution_result.outcome}")
            else:
                print(f"Agent requesting input: {result.agent_message}")
                # Send response
                client.add_message_to_execution(execution_id, "user response")
                # Wait again
                result = client.wait_for_agent_interaction(execution_id)
        """
        # Validate parameters
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise TimeoutError(f"Wait for interaction on execution {execution_id} timed out after {timeout}s")

            # Get current execution state
            execution = self.get_execution(execution_id)
            current_status = execution.status
            status_str = current_status.value.lower()

            # Handle terminal states
            if current_status == ExecutionStatus.COMPLETED:
                if execution.execution_result:
                    return AgentInteractionResult(
                        is_terminal=True,
                        status=status_str,
                        agent_message=None,
                        execution_result=execution.execution_result
                    )
                # Execution completed but result not ready yet, wait a bit more
                time.sleep(poll_interval)
                continue

            elif current_status in [ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                return AgentInteractionResult(
                    is_terminal=True,
                    status=status_str,
                    agent_message=None,
                    execution_result=execution.execution_result
                )

            # Handle agent interaction request
            elif current_status == ExecutionStatus.PAUSED_BY_AGENT:
                # Get the agent's message/request
                agent_message = self._extract_agent_request_message(execution_id)
                return AgentInteractionResult(
                    is_terminal=False,
                    status=status_str,
                    agent_message=agent_message,
                    execution_result=None
                )

            # Wait before next poll for non-terminal, non-interaction states
            time.sleep(poll_interval)

    def _extract_agent_request_message(self, execution_id: str) -> str:
        """
        Extract the agent's request message from recent activities.

        Args:
            execution_id: The execution identifier

        Returns:
            The agent's message or a default message if not found
        """
        try:
            activities = self.get_last_n_execution_activities(execution_id, 20)

            # Filter for human input requests
            human_input_requests = [
                activity for activity in activities
                if (hasattr(activity, 'payload') and
                    activity.payload and
                    getattr(activity.payload, 'activityType', None) == 'action_started')
            ]

            if human_input_requests:
                human_input_request = human_input_requests[0]

                # Extract message from payload data with robust error handling
                try:
                    payload = human_input_request.payload
                    if hasattr(payload, 'data') and payload.data:
                        payload_data = payload.data
                        if hasattr(payload_data, 'message') and payload_data.message:
                            return str(payload_data.message)
                    return 'Agent is requesting input'
                except (AttributeError, TypeError) as e:
                    return 'Agent is requesting input (extraction failed)'

            return 'Agent is requesting input'

        except AsteroidAPIError as e:
            return 'Agent is requesting input (API error)'
        except Exception as e:
            return 'Agent is requesting input (extraction failed)'

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """Context manager exit: clean up API client connection pool."""
        try:
            # Try to grab the pool_manager; if any attr is missing, skip
            try:
                pool_manager = self.api_client.rest_client.pool_manager
            except AttributeError:
                pool_manager = None

            if pool_manager:
                pool_manager.clear()
        except Exception as e:
            pass
        return False

    def get_agents(self, org_id: str, page: int = 1, page_size: int = 100) -> List[Agent]:
        """
        Get a paginated list of agents for an organization.
        Args:
            org_id: The organization identifier
            page: The page number
            page_size: The page size
        Returns:
            A list of agents
        Raises:
            Exception: If the agents request fails
        Example:
            agents = client.get_agents("org_id", page=1, page_size=100)
            for agent in agents:
                print(f"Agent: {agent.name}")
        """
        response = self.agents_v2_agents_api.agent_list(organization_id=org_id, page=page, page_size=page_size)
        return response.items

    def get_executions(
        self,
        organization_id: str,
        page: int = 1,
        page_size: int = 20,
        execution_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[List[str]] = None,
        agent_version: Optional[int] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        human_labels: Optional[List[str]] = None,
        outcome_label: Optional[str] = None,
        metadata_key: Optional[str] = None,
        metadata_value: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
    ) -> ExecutionsList200Response:
        """
        Get a paginated list of executions with optional filtering.

        Args:
            organization_id: The organization identifier (required)
            page: The page number (default: 1)
            page_size: The page size (default: 20)
            execution_id: Search by execution ID (partial, case-insensitive match)
            agent_id: Filter by agent ID
            status: Filter by execution status (can specify multiple)
            agent_version: Filter by agent version
            created_after: Filter executions created after this timestamp (ISO 8601)
            created_before: Filter executions created before this timestamp (ISO 8601)
            human_labels: Filter by human labels (can specify multiple label IDs)
            outcome_label: Filter by execution result outcome (partial, case-insensitive match)
            metadata_key: Filter by metadata key - must be used together with metadata_value
            metadata_value: Filter by metadata value - must be used together with metadata_key
            sort_field: Field to sort by (e.g., 'created_at')
            sort_direction: Sort direction ('asc' or 'desc')

        Returns:
            Paginated execution list with metadata

        Raises:
            AsteroidAPIError: If the executions request fails

        Example:
            # Get all executions for an organization
            result = client.get_executions(organization_id='org_123', page=1, page_size=20)

            # Filter by agent and status
            result = client.get_executions(
                organization_id='org_123',
                agent_id='agent_456',
                status=['completed', 'failed'],
                sort_field='created_at',
                sort_direction='desc'
            )
        """
        from datetime import datetime as dt

        # Convert status strings to enum if provided
        status_enums = None
        if status:
            status_enums = [ExecutionStatus(s) for s in status]

        # Convert sort_field and sort_direction to enums if provided
        sort_field_enum = ExecutionSortField(sort_field) if sort_field else None
        sort_direction_enum = SortDirection(sort_direction) if sort_direction else None

        # Parse datetime strings
        created_after_dt = dt.fromisoformat(created_after.replace('Z', '+00:00')) if created_after else None
        created_before_dt = dt.fromisoformat(created_before.replace('Z', '+00:00')) if created_before else None

        try:
            return self.agents_v2_execution_api.executions_list(
                page_size=page_size,
                page=page,
                organization_id=organization_id,
                execution_id=execution_id,
                agent_id=agent_id,
                status=status_enums,
                agent_version=agent_version,
                created_after=created_after_dt,
                created_before=created_before_dt,
                human_labels=human_labels,
                outcome_label=outcome_label,
                metadata_key=metadata_key,
                metadata_value=metadata_value,
                sort_field=sort_field_enum,
                sort_direction=sort_direction_enum,
            )
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get executions: {e}") from e

    def get_last_n_execution_activities(self, execution_id: str, n: int) -> List[ExecutionActivity]:
        """
        Get the last N execution activities for a given execution ID, sorted by their timestamp in descending order.
        Args:
            execution_id: The execution identifier
            n: The number of activities to return
        Returns:
            A list of execution activities
        Raises:
            Exception: If the execution activities request fails
        """
        return self.agents_v2_execution_api.execution_activities_get(execution_id, order="desc", limit=n)
    def add_message_to_execution(self, execution_id: str, message: str) -> None:
        """
        Add a message to an execution.
        Args:
            execution_id: The execution identifier
            message: The message to add
        Returns:
            None
        Raises:
            Exception: If the message addition fails
        Example:
            add_message_to_execution(client, "execution_id", "Hello, world!")
        """
        message_body = ExecutionUserMessagesAddTextBody(message=message)
        return self.agents_v2_execution_api.execution_user_messages_add(execution_id, message_body)

    def get_execution_files(self, execution_id: str) -> List[File]:
        """
        Get a list of files associated with an execution.
        Args:
            execution_id: The execution identifier
        Returns:
            A list of files associated with the execution
        Raises:
            AsteroidAPIError: If the files request fails
        Example:
            files = client.get_execution_files("execution_id")
            for file in files:
                print(f"File: {file.file_name}, Size: {file.file_size}")
        """
        try:
            return self.agents_v2_files_api.execution_context_files_get(execution_id)
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to get execution files: {e}") from e

    def stage_temp_files(
        self,
        organization_id: str,
        files: List[Union[bytes, str, Tuple[str, bytes]]],
        default_filename: str = "file.txt"
    ) -> List[TempFile]:
        """
        Stage files before starting an execution.

        Use this method to pre-upload files that will be attached to an execution when it starts.
        The returned TempFile objects can be passed to execute_agent's temp_files parameter.

        Args:
            organization_id: The organization identifier
            files: List of files to stage. Each file can be:
                   - bytes: Raw file content (will use default_filename)
                   - str: File path as string (will read file and use filename)
                   - Tuple[str, bytes]: (filename, file_content) tuple
            default_filename: Default filename to use when file is provided as bytes

        Returns:
            List of TempFile objects that can be passed to execute_agent

        Raises:
            AsteroidAPIError: If the staging request fails

        Example:
            # Stage files before execution
            temp_files = client.stage_temp_files("org-123", [
                ("data.csv", csv_content.encode()),
                "/path/to/document.pdf"
            ])

            # Use staged files when executing agent
            execution_id = client.execute_agent(
                agent_id="my-agent",
                execution_data={"input": "Process these files"},
                temp_files=temp_files
            )
        """
        try:
            # Process files to ensure proper format for the V2 API
            processed_files = []
            for file_item in files:
                if isinstance(file_item, tuple):
                    # Already in (filename, content) format
                    filename, content = file_item
                    if isinstance(content, str):
                        content = content.encode()
                    processed_files.append((filename, content))
                elif isinstance(file_item, str):
                    # Check if string is a file path that exists, otherwise treat as content
                    if os.path.isfile(file_item):
                        # File path - read the file
                        filename = os.path.basename(file_item)
                        with open(file_item, 'rb') as f:
                            content = f.read()
                        processed_files.append((filename, content))
                    else:
                        # String content - encode and use default filename
                        content = file_item.encode()
                        processed_files.append((default_filename, content))
                elif isinstance(file_item, bytes):
                    # Raw bytes - use default filename
                    processed_files.append((default_filename, file_item))
                else:
                    # Other types - convert to string content and encode
                    content = str(file_item).encode()
                    processed_files.append((default_filename, content))

            response = self.agents_v2_files_api.temp_files_stage(organization_id, files=processed_files)
            return response.temp_files
        except ApiException as e:
            raise AsteroidAPIError(f"Failed to stage temp files: {e}") from e

    def download_execution_file(self, file: File, download_path: Union[str, Path],
                              create_dirs: bool = True, timeout: int = 30) -> str:
        """
        Download a file from an execution using its signed URL.

        Args:
            file: The File object containing the signed URL and metadata
            download_path: Path where the file should be saved. Can be a directory or full file path
            create_dirs: Whether to create parent directories if they don't exist (default: True)
            timeout: Request timeout in seconds (default: 30)

        Returns:
            The full path where the file was saved

        Raises:
            AsteroidAPIError: If the download fails
            FileNotFoundError: If the parent directory doesn't exist and create_dirs is False

        Example:
            files = client.get_execution_files("execution_id")
            for file in files:
                # Download to specific directory
                saved_path = client.download_execution_file(file, "/path/to/downloads/")
                print(f"Downloaded {file.file_name} to {saved_path}")

                # Download with specific filename
                saved_path = client.download_execution_file(file, "/path/to/downloads/my_file.txt")
                print(f"Downloaded to {saved_path}")
        """
        final_path = None
        try:
            # Convert to Path object for easier manipulation
            download_path = Path(download_path)

            # Determine the final file path
            if download_path.is_dir() or str(download_path).endswith('/'):
                # If download_path is a directory, use the original filename
                final_path = download_path / file.file_name
            else:
                # If download_path includes a filename, use it as-is
                final_path = download_path

            # Create parent directories if needed
            if create_dirs:
                final_path.parent.mkdir(parents=True, exist_ok=True)
            elif not final_path.parent.exists():
                raise FileNotFoundError(f"Parent directory does not exist: {final_path.parent}")

            # Download the file using the signed URL
            response = requests.get(file.signed_url, timeout=timeout, stream=True)
            response.raise_for_status()

            # Verify content length if available
            expected_size = file.file_size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) != expected_size:
                raise AsteroidAPIError(
                    f"Content length mismatch: expected {expected_size}, got {content_length}"
                )

            # Write the file in chunks to handle large files efficiently
            chunk_size = 8192
            total_size = 0

            with open(final_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        total_size += len(chunk)

            # Final verification of the downloaded file size
            if total_size != expected_size:
                raise AsteroidAPIError(
                    f"Downloaded file size mismatch: expected {expected_size}, got {total_size}"
                )

            return str(final_path)

        except requests.exceptions.RequestException as e:
            # Clean up partial file on network error
            if final_path and final_path.exists():
                final_path.unlink(missing_ok=True)
            raise AsteroidAPIError(f"Failed to download file {file.file_name}: {e}") from e
        except OSError as e:
            # Clean up partial file on I/O error
            if final_path and final_path.exists():
                final_path.unlink(missing_ok=True)
            raise AsteroidAPIError(f"Failed to save file {file.file_name}: {e}") from e
        except AsteroidAPIError:
            # Clean up partial file on size mismatch or other API errors
            if final_path and final_path.exists():
                final_path.unlink(missing_ok=True)
            raise
        except Exception as e:
            # Clean up partial file on unexpected error
            if final_path and final_path.exists():
                final_path.unlink(missing_ok=True)
            raise AsteroidAPIError(f"Unexpected error downloading file {file.file_name}: {e}") from e

# Convenience functions that mirror the TypeScript SDK pattern
def create_client(api_key: str, base_url: Optional[str] = None) -> AsteroidClient:
    """
    Create an API client with a provided API key.

    This is a convenience function that creates an AsteroidClient instance.

    Args:
        api_key: Your API key
        base_url: Optional base URL

    Returns:
        A configured AsteroidClient instance

    Example:
        client = create_client('your-api-key')
    """
    return AsteroidClient(api_key, base_url)

# --- V2 ---

def execute_agent(
    client: AsteroidClient,
    agent_id: str,
    dynamic_data: Optional[Dict[str, Any]] = None,
    agent_profile_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    temp_files: Optional[List[TempFile]] = None,
    version: Optional[int] = None,
) -> str:
    """
    Execute an agent with the provided parameters.

    Args:
        client: The AsteroidClient instance
        agent_id: The ID of the agent to execute
        dynamic_data: Dynamic data to be merged into the placeholders defined in prompts
        agent_profile_id: Optional ID of the agent profile to use
        metadata: Optional metadata key-value pairs for organizing and filtering executions
        temp_files: Optional list of temporary files to attach (must be pre-uploaded using stage_temp_files)
        version: Optional version of the agent to execute. If not provided, the latest version will be used.

    Returns:
        The execution ID

    Example:
        execution_id = execute_agent(client, 'my-agent-id', {'input': 'some dynamic value'})
        execution_id = execute_agent(client, 'my-agent-id', {'input': 'value'}, version=3)
    """
    return client.execute_agent(
        agent_id,
        dynamic_data,
        agent_profile_id,
        metadata,
        temp_files,
        version,
    )

def get_execution(client: AsteroidClient, execution_id: str) -> ExecutionListItem:
    """
    Get a single execution by ID with all details.

    This function returns comprehensive execution information including status,
    result, browser recording URL, and other metadata.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier

    Returns:
        The execution details including:
        - status: Current execution status
        - execution_result: Result with outcome and reasoning (if terminal)
        - browser_recording_url: Recording URL (if browser session was used)
        - browser_live_view_url: Live view URL (if execution is running)
        - agent_id, agent_name, agent_version: Agent information
        - created_at, terminal_at, duration: Timing information
        - metadata, comments, human_labels: Additional data

    Raises:
        AsteroidAPIError: If the request fails

    Example:
        execution = get_execution(client, execution_id)
        print(f"Status: {execution.status}")
        if execution.execution_result:
            print(f"Outcome: {execution.execution_result.outcome}")
        if execution.browser_recording_url:
            print(f"Recording: {execution.browser_recording_url}")
    """
    return client.get_execution(execution_id)


def wait_for_execution_result(
    client: AsteroidClient,
    execution_id: str,
    interval: float = 1.0,
    timeout: float = 3600.0
) -> ExecutionResult:
    """
    Wait for an execution to reach a terminal state and return the result.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        interval: Polling interval in seconds (default is 1.0)
        timeout: Maximum wait time in seconds (default is 3600 - 1 hour)

    Returns:
        The execution result object

    Raises:
        TimeoutError: If the execution times out
        ExecutionError: If the execution ends as "cancelled" or "failed"

    Example:
        result = wait_for_execution_result(client, execution_id, interval=2.0)
        print(result.outcome, result.reasoning)
    """
    return client.wait_for_execution_result(execution_id, interval, timeout)


def upload_execution_files(
    client: AsteroidClient,
    execution_id: str,
    files: List[Union[bytes, str, Tuple[str, bytes]]],
    default_filename: str = "file.txt"
) -> str:
    """
    Upload files to a running execution.

    Use this function to upload files to an execution that is already in progress.
    If you want to attach files to an execution before it starts, use stage_temp_files instead.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        files: List of files to upload
        default_filename: Default filename to use when file is provided as bytes

    Returns:
        Success message from the API

    Example:
        # Create a simple text file with "Hello World!" content
        hello_content = "Hello World!".encode()
        response = upload_execution_files(client, execution_id, [hello_content])

        # Or specify filename with content
        files = [('hello.txt', "Hello World!".encode())]
        response = upload_execution_files(client, execution_id, files)
    """
    return client.upload_execution_files(execution_id, files, default_filename)


def stage_temp_files(
    client: AsteroidClient,
    organization_id: str,
    files: List[Union[bytes, str, Tuple[str, bytes]]],
    default_filename: str = "file.txt"
) -> List[TempFile]:
    """
    Stage files before starting an execution.

    Use this function to pre-upload files that will be attached to an execution when it starts.
    The returned TempFile objects can be passed to execute_agent's temp_files parameter.

    Args:
        client: The AsteroidClient instance
        organization_id: The organization identifier
        files: List of files to stage. Each file can be:
               - bytes: Raw file content (will use default_filename)
               - str: File path as string (will read file and use filename)
               - Tuple[str, bytes]: (filename, file_content) tuple
        default_filename: Default filename to use when file is provided as bytes

    Returns:
        List of TempFile objects that can be passed to execute_agent

    Raises:
        AsteroidAPIError: If the staging request fails

    Example:
        # Stage files before execution
        temp_files = stage_temp_files(client, "org-123", [
            ("data.csv", csv_content.encode()),
            "/path/to/document.pdf"
        ])

        # Use staged files when executing agent
        execution_id = execute_agent(
            client,
            agent_id="my-agent",
            execution_data={"input": "Process these files"},
            temp_files=temp_files
        )
    """
    return client.stage_temp_files(organization_id, files, default_filename)


# --- V1 (Agent Profiles) ---

def get_agent_profiles(client: AsteroidClient, organization_id: Optional[str] = None) -> List[AgentProfile]:
    """
    Get a list of agent profiles.
    Args:
        client: The AsteroidClient instance
        organization_id: The organization identifier (optional) Returns all agent profiles if no organization_id is provided.
    Returns:
        A list of agent profiles
    Raises:
        Exception: If the agent profiles request fails
    Example:
        profiles = get_agent_profiles(client, "org-123")
    """
    return client.get_agent_profiles(organization_id)
def get_agent_profile(client: AsteroidClient, profile_id: str) -> AgentProfile:
    """
    Get an agent profile by ID.
    Args:
        client: The AsteroidClient instance
        profile_id: The ID of the agent profile
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile request fails
    Example:
        profile = get_agent_profile(client, "profile_id")
    """
    return client.get_agent_profile(profile_id)
def create_agent_profile(client: AsteroidClient, request: CreateAgentProfileRequest) -> AgentProfile:
    """
    Create an agent profile.
    Args:
        client: The AsteroidClient instance
        request: The request object
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile creation fails
    Example:
        request = CreateAgentProfileRequest(
            name="My Agent Profile",
            description="This is my agent profile",
            organization_id="org-123",
            proxy_cc=CountryCode.US,
            proxy_type=ProxyType.RESIDENTIAL,
            captcha_solver_active=True,
            sticky_ip=True,
            credentials=[Credential(name="user", data="password")]
        )
        profile = create_agent_profile(client, request)
    """
    return client.create_agent_profile(request)
def update_agent_profile(client: AsteroidClient, profile_id: str, request: UpdateAgentProfileRequest) -> AgentProfile:
    """
    Update an agent profile with the provided request.
    Args:
        client: The AsteroidClient instance
        profile_id: The ID of the agent profile
        request: The request object
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile update fails
    Example:
        request = UpdateAgentProfileRequest(
            name="My Agent Profile",
            description="This is my agent profile",
            organization_id="org-123",
        )
        profile = update_agent_profile(client, "profile_id", request)
    """
    return client.update_agent_profile(profile_id, request)
def delete_agent_profile(client: AsteroidClient, profile_id: str) -> DeleteAgentProfile200Response:
    """
    Delete an agent profile.
    Args:
        client: The AsteroidClient instance
        profile_id: The ID of the agent profile
    Returns:
        The agent profile
    Raises:
        Exception: If the agent profile deletion fails
    Example:
        profile_deleted =delete_agent_profile(client, "profile_id")
    """
    return client.delete_agent_profile(profile_id)

def get_credentials_public_key(client: AsteroidClient) -> str:
    """
    Get the public key for encrypting credentials.

    Args:
        client: The AsteroidClient instance

    Returns:
        PEM-formatted RSA public key string

    Example:
        public_key = get_credentials_public_key(client)
    """
    return client.get_credentials_public_key()

# --- V2 ---

def get_agents(client: AsteroidClient, org_id: str, page: int = 1, page_size: int = 100) -> List[Agent]:
    """
    Get a paginated list of agents for an organization.
    Args:
        client: The AsteroidClient instance
        org_id: The organization identifier
        page: The page number
        page_size: The page size
    Returns:
        A list of agents
    Raises:
        Exception: If the agents request fails
    Example:
        agents = get_agents(client, "org_id", page=1, page_size=100)
        for agent in agents:
            print(f"Agent: {agent.name}")
    """
    return client.get_agents(org_id, page, page_size)

def get_executions(
    client: AsteroidClient,
    organization_id: str,
    page: int = 1,
    page_size: int = 20,
    execution_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    status: Optional[List[str]] = None,
    agent_version: Optional[int] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    human_labels: Optional[List[str]] = None,
    outcome_label: Optional[str] = None,
    metadata_key: Optional[str] = None,
    metadata_value: Optional[str] = None,
    sort_field: Optional[str] = None,
    sort_direction: Optional[str] = None,
) -> ExecutionsList200Response:
    """
    Get a paginated list of executions with optional filtering.

    Args:
        client: The AsteroidClient instance
        organization_id: The organization identifier (required)
        page: The page number (default: 1)
        page_size: The page size (default: 20)
        execution_id: Search by execution ID (partial, case-insensitive match)
        agent_id: Filter by agent ID
        status: Filter by execution status (can specify multiple)
        agent_version: Filter by agent version
        created_after: Filter executions created after this timestamp (ISO 8601)
        created_before: Filter executions created before this timestamp (ISO 8601)
        human_labels: Filter by human labels (can specify multiple label IDs)
        outcome_label: Filter by execution result outcome (partial, case-insensitive match)
        metadata_key: Filter by metadata key - must be used together with metadata_value
        metadata_value: Filter by metadata value - must be used together with metadata_key
        sort_field: Field to sort by (e.g., 'created_at')
        sort_direction: Sort direction ('asc' or 'desc')

    Returns:
        Paginated execution list with metadata

    Example:
        result = get_executions(client, organization_id='org_123', page=1, page_size=20)
    """
    return client.get_executions(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
        execution_id=execution_id,
        agent_id=agent_id,
        status=status,
        agent_version=agent_version,
        created_after=created_after,
        created_before=created_before,
        human_labels=human_labels,
        outcome_label=outcome_label,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        sort_field=sort_field,
        sort_direction=sort_direction,
    )

def get_last_n_execution_activities(client: AsteroidClient, execution_id: str, n: int) -> List[ExecutionActivity]:
    """
    Get the last N execution activities for a given execution ID, sorted by their timestamp in descending order.
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        n: The number of activities to return
    Returns:
        A list of execution activities
    Raises:
        Exception: If the execution activities request fails
    Example:
        activities = get_last_n_execution_activities(client, "execution_id", 10)
    """
    return client.get_last_n_execution_activities(execution_id, n)

def add_message_to_execution(client: AsteroidClient, execution_id: str, message: str) -> None:
    """
    Add a message to an execution.
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        message: The message to add
    Returns:
        None
    Raises:
        Exception: If the message addition fails
    Example:
        add_message_to_execution(client, "execution_id", "Hello, world!")
    """
    return client.add_message_to_execution(execution_id, message)

def get_execution_files(client: AsteroidClient, execution_id: str) -> List[File]:
    """
    Get a list of files associated with an execution.
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
    Returns:
        A list of files associated with the execution
    Raises:
        Exception: If the files request fails
    Example:
        files = get_execution_files(client, "execution_id")
        for file in files:
            print(f"File: {file.file_name}, Size: {file.file_size}")
    """
    return client.get_execution_files(execution_id)

def download_execution_file(client: AsteroidClient, file: File, download_path: Union[str, Path],
                          create_dirs: bool = True, timeout: int = 30) -> str:
    """
    Download a file from an execution using its signed URL.

    Args:
        client: The AsteroidClient instance
        file: The File object containing the signed URL and metadata
        download_path: Path where the file should be saved. Can be a directory or full file path
        create_dirs: Whether to create parent directories if they don't exist (default: True)
        timeout: Request timeout in seconds (default: 30)

    Returns:
        The full path where the file was saved

    Raises:
        AsteroidAPIError: If the download fails
        FileNotFoundError: If the parent directory doesn't exist and create_dirs is False

    Example:
        files = get_execution_files(client, "execution_id")
        for file in files:
            # Download to specific directory
            saved_path = download_execution_file(client, file, "/path/to/downloads/")
            print(f"Downloaded {file.file_name} to {saved_path}")

            # Download with specific filename
            saved_path = download_execution_file(client, file, "/path/to/downloads/my_file.txt")
            print(f"Downloaded to {saved_path}")
    """
    return client.download_execution_file(file, download_path, create_dirs, timeout)



def wait_for_agent_interaction(
    client: AsteroidClient,
    execution_id: str,
    poll_interval: float = 2.0,
    timeout: float = 3600.0
) -> AgentInteractionResult:
    """
    Wait for an agent interaction request or terminal state.

    This convenience function provides the same functionality as the AsteroidClient.wait_for_agent_interaction method.

    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier for an already started execution
        poll_interval: How often to check for updates in seconds (default: 2.0)
        timeout: Maximum wait time in seconds (default: 3600 - 1 hour)

    Returns:
        AgentInteractionResult containing:
        - is_terminal: True if execution finished (completed/failed/cancelled)
        - status: Current execution status string
        - agent_message: Agent's message if requesting interaction (None if terminal)
        - execution_result: Final result if terminal state (None if requesting interaction)

    Raises:
        ValueError: If interval or timeout parameters are invalid
        TimeoutError: If the execution times out
        AsteroidAPIError: If API calls fail

    Example:
        # Start an execution first
        execution_id = execute_agent(client, 'agent-id', {'input': 'test'})

        # Wait for interaction or completion
        result = wait_for_agent_interaction(client, execution_id)

        if result.is_terminal:
            print(f"Execution finished with status: {result.status}")
            if result.execution_result:
                print(f"Result: {result.execution_result.outcome}")
        else:
            print(f"Agent requesting input: {result.agent_message}")
            # Send response
            add_message_to_execution(client, execution_id, "user response")
            # Wait again
            result = wait_for_agent_interaction(client, execution_id)
    """
    return client.wait_for_agent_interaction(
        execution_id=execution_id,
        poll_interval=poll_interval,
        timeout=timeout
    )

# Re-export common types for convenience
__all__ = [
    # Client
    'AsteroidClient',
    'create_client',
    # Agent Execution (V2)
    'execute_agent',
    'get_execution',
    'get_executions',
    'wait_for_execution_result',
    'upload_execution_files',
    'stage_temp_files',
    # Agent Profiles (V1)
    'get_agent_profiles',
    'get_agent_profile',
    'create_agent_profile',
    'update_agent_profile',
    'delete_agent_profile',
    'get_credentials_public_key',
    # Agents (V2)
    'get_agents',
    # Execution Activities (V2)
    'get_last_n_execution_activities',
    'add_message_to_execution',
    'get_execution_files',
    'download_execution_file',
    'wait_for_agent_interaction',
    # Exceptions
    'AsteroidAPIError',
    'ExecutionError',
    'TimeoutError',
    'AgentInteractionResult',
    # Types
    'TempFile',
    'TempFilesResponse',
    'ExecuteAgentRequest',
    'ExecutionListItem',
    'ExecutionResult',
    'ExecutionsList200Response',
    'ExecutionStatus',
    'ExecutionSortField',
    'SortDirection',
]
