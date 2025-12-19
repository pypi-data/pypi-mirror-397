# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Utility functions for agent demos
"""

import os
from typing import Optional

from certiv.logger import logger


def register_user(
    username: str,
    password: str,
    endpoint: str,
    email: str = None,
) -> tuple[bool, Optional[str]]:
    """Register a new user account with immediate login capability

    Args:
        username: Username for the new account
        password: Password for the new account
        email: Email address (defaults to username@certiv.ai)

    Returns:
        Tuple of (success: bool, token: Optional[str])
        When password is provided, registration returns a token for immediate login
    """
    import requests

    if email is None:
        # Only append @certiv.ai if username doesn't already contain @
        email = username if "@" in username else f"{username}@certiv.ai"

    response = requests.post(
        f"{endpoint}/auth/register",
        json={
            "username": username,
            "password": password,
            "email": email,
        },
        timeout=30,
    )

    if response.status_code in [200, 201]:
        logger.info(f"Successfully registered user: {username}")

        # When password is provided, backend returns token for immediate login
        response_data = response.json()
        token = response_data.get("token")

        # Handle nested token format: {"token": {"token": "actual_jwt", ...}}
        if isinstance(token, dict):
            token = token.get("token")

        if token:
            logger.info("Registration returned auth token for immediate login")
            logger.debug(f"Token (first 50 chars): {str(token)[:50]}...")
        else:
            logger.warn(
                "Registration successful but no token returned (password may not have been set)"
            )

        return True, token
    else:
        logger.warn(f"Failed to register user {username}: {response.text}")
        return False, None


def login_admin(
    username: str,
    password: str,
    endpoint: str,
    auto_register: bool = True,
) -> tuple[str, bool]:
    """Login as admin and get authentication token

    Args:
        username: Admin username (will be converted to email for login)
        password: Admin password
        auto_register: If True, attempt to register user if login fails

    Returns:
        Tuple of (authentication_token, was_new_user_created)
    """
    import requests

    # Convert username to email format for login endpoint
    # The backend login endpoint expects "email" field, not "username"
    email = f"{username}@certiv.ai" if "@" not in username else username

    response = requests.post(
        f"{endpoint}/auth/login",
        json={"email": email, "password": password},
        timeout=30,
    )

    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            print(f"   ✓ Successfully logged in as {username}")
            logger.info("Successfully authenticated")
            return token, False  # Existing user, not newly created
        else:
            raise Exception("Failed to get auth token from response")

    # If login failed and auto_register is enabled, try to register first
    if response.status_code == 401 and auto_register:
        print(f"   User {username} doesn't exist, creating account...")
        logger.info(f"Login failed for {username}, attempting to register user...")

        success, token = register_user(username, password, endpoint)
        if success:
            print(f"   ✓ Account created for {username}")

            # Registration with password returns a token, so we can use it directly
            if token:
                print("   ✓ Using auth token from registration")
                logger.info("Successfully authenticated via registration response")
                return token, True  # New user was created
            else:
                # Fallback: try to login if registration didn't return a token
                logger.warn(
                    "Registration succeeded but didn't return token, trying login..."
                )
                retry_response = requests.post(
                    f"{endpoint}/auth/login",
                    json={"email": email, "password": password},
                    timeout=30,
                )

                if retry_response.status_code == 200:
                    retry_data = retry_response.json()
                    token = retry_data.get("token")
                    if isinstance(token, dict):
                        token = token.get("token")

                    if token:
                        print(f"   ✓ Successfully logged in as {username}")
                        logger.info("Successfully authenticated after registration")
                        return token, True
                    else:
                        raise Exception("Failed to get auth token after registration")
                else:
                    raise Exception(
                        f"Login failed even after registration: {retry_response.text}"
                    )
        else:
            raise Exception(f"Both login and registration failed for user {username}")

    # If we get here, login failed and either auto_register is disabled or registration failed
    raise Exception(f"Failed to login: {response.text}")


def get_user_default_organization(token: str, endpoint: str) -> str:
    """Get the user's default organization

    Args:
        token: User authentication token

    Returns:
        organization_id of the user's default organization
    """
    import requests

    try:
        response = requests.get(
            f"{endpoint}/organizations/my",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )

        if response.status_code == 200:
            orgs = response.json()
            logger.debug(f"Organizations response: {orgs}")

            if isinstance(orgs, dict) and "organizations" in orgs:
                orgs_list = orgs["organizations"]
            elif isinstance(orgs, list):
                orgs_list = orgs
            else:
                orgs_list = []

            logger.info(f"Found {len(orgs_list)} organizations for user")

            # Find the user's default organization (usually the first one or marked as default)
            if orgs_list:
                # Prefer organization with 'personal' type or the first one
                default_org = None
                for org in orgs_list:
                    if org.get("type") == "personal":
                        default_org = org
                        break

                if not default_org:
                    default_org = orgs_list[0]

                org_id = default_org.get("id") or default_org.get("organization_id")
                org_name = default_org.get("name") or default_org.get(
                    "display_name", "Unknown"
                )

                if org_id:
                    logger.info(
                        f"Using user's default organization: {org_name} ({org_id})"
                    )
                    return org_id

            raise Exception("No organizations found for user")
        else:
            logger.error(
                f"Failed to fetch organizations: {response.status_code} - {response.text}"
            )
            raise Exception(
                f"Failed to fetch organizations: {response.status_code} - {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"Request error fetching organizations: {e}")
        raise Exception(f"Could not fetch user's organizations: {e}") from e
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        raise Exception(f"Could not fetch user's organizations: {e}") from e


def create_organization(
    token: str,
    endpoint: str,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Create an organization and return organization_id

    Args:
        token: Admin authentication token
        name: Unique organization identifier (slug format)
        display_name: Human-readable organization name
        description: Optional organization description

    Returns:
        organization_id
    """
    import time

    import requests

    if name is None:
        name = f"sdk-demo-org-{int(time.time())}"

    if display_name is None:
        display_name = f"SDK Demo Organization {int(time.time())}"

    if description is None:
        description = "Organization created by SDK for testing"

    response = requests.post(
        f"{endpoint}/organizations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "display_name": display_name,
            "description": description,
            "type": "standard",
        },
        timeout=30,
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to create organization: {response.text}")

    data = response.json()
    organization_id = data["id"]

    logger.info(f"Created organization: {organization_id}")

    # The creating user should automatically be added as owner,
    # but let's verify by checking if we can list the organization
    try:
        verify_response = requests.get(
            f"{endpoint}/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if verify_response.status_code == 200:
            logger.info("Organization access verified for user")
        else:
            logger.warn(
                f"Cannot access created organization: {verify_response.status_code} - {verify_response.text}"
            )
    except Exception as e:
        logger.warn(f"Failed to verify organization access: {e}")

    return organization_id


def set_current_organization(
    token: str,
    organization_id: str,
    endpoint: str,
) -> bool:
    """Set the user's current organization in preferences

    Args:
        token: User authentication token
        organization_id: Organization ID to set as current

    Returns:
        True if successful
    """
    import requests

    response = requests.put(
        f"{endpoint}/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_organization_id": organization_id,
        },
        timeout=30,
    )

    if response.status_code not in [200, 201]:
        logger.warn(f"Failed to set current organization: {response.text}")
        return False

    logger.info(f"Set current organization to: {organization_id}")
    return True


def create_stear_group(
    token: str,
    endpoint: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> tuple[str, str]:
    """Create a STEAR group and return stear_group_id and registration_secret

    Args:
        token: Admin authentication token
        name: Name for the STEAR group (will be auto-generated if not provided)
        description: Description for the STEAR group

    Returns:
        Tuple of (stear_group_id, registration_secret)
    """
    import time

    import requests

    if name is None:
        name = f"SDK Demo Group {int(time.time())}"

    if description is None:
        description = "STEAR group created by SDK"

    headers = {"Authorization": f"Bearer {token}"}

    # If organization_id is provided, use the organization-specific endpoint
    if organization_id:
        url = f"{endpoint}/organizations/{organization_id}/stear-groups"
    else:
        # Fallback to the general endpoint (though this will likely fail now)
        url = f"{endpoint}/stear"

    response = requests.post(
        url,
        headers=headers,
        json={
            "name": name,
            "description": description,
            "agent_approval_mode": "automatic",
            "agent_settings": {"max_agents": 50, "require_agent_review": False},
        },
        timeout=30,
    )

    if response.status_code not in [200, 201]:
        # Print more debug info
        logger.error(f"STEAR creation failed with status {response.status_code}")
        logger.error(f"URL used: {url}")
        logger.error("Request payload: {'name': name, 'description': description}")
        logger.error(f"Response: {response.text}")
        raise Exception(f"Failed to create STEAR group: {response.text}")

    # Handle different response formats
    data = response.json()
    if "stear_group" in data:
        stear_group_id = data["stear_group"]["stear_group_id"]
        registration_secret = data.get("registration_secret", {}).get("secret", "")
    else:
        stear_group_id = data.get("stear_group_id") or data.get("id")
        registration_secret = data.get("registration_secret", "")

    logger.info(f"Created STEAR group: {stear_group_id}")
    return stear_group_id, registration_secret


def setup_agent_credentials(
    endpoint: str,
    username: str = None,
    password: str = None,
    save_to_env: bool = True,
    env_file: str = ".env.local",
) -> tuple[str, str, str]:
    """Setup agent credentials by creating new STEAR group and agent

    This is the generalized version of --create-agent functionality that:
    1. Logs in as admin (with auto-registration)
    2. Gets user's default organization
    3. Creates a new STEAR group in that organization
    4. Creates a new agent in the new STEAR group
    5. Optionally saves credentials to .env file

    Args:
        username: Admin username (defaults to environment var or 'magos-test')
        password: Admin password (defaults to environment var or 'magosmagos1')
        save_to_env: Whether to save credentials to env file
        env_file: Path to env file for saving credentials

    Returns:
        Tuple of (agent_id, agent_secret, stear_group_id)
    """
    import time

    # Get admin credentials - try parameters, then environment, then defaults
    if username is None:
        username = os.getenv("ADMIN_USERNAME", "magos-test")

    if password is None:
        password = os.getenv("ADMIN_PASSWORD", "magosmagos1")

    # Store the original username (without domain) for registration
    original_username = username.split("@")[0] if "@" in username else username

    # Ensure username is in email format for login
    if username and "@" not in username:
        username = f"{username}@certiv.ai"

    try:
        # Configure logging to see registration messages
        logger.set_log_level("debug")

        # Login as admin (with auto-registration if needed)
        print("🔐 Setting up agent credentials...")
        print(f"   Username: {username}")
        token, is_new_user = login_admin(
            original_username, password, endpoint, auto_register=True
        )

        # Get user's default organization and STEAR group
        print("🏢 Finding user's default organization...")

        try:
            org_id = get_user_default_organization(token, endpoint)
            print(f"   ✓ Found default organization: {org_id}")

            # Set the organization as the current one
            print("🔄 Setting current organization...")
            if set_current_organization(token, org_id, endpoint):
                print("   ✓ Current organization set")
            else:
                print("   ⚠️  Failed to set current organization, but continuing...")

        except Exception as e:
            print(f"   ⚠️  No default organization found: {e}")
            print("   Creating a new organization...")

            # Fallback: Create an organization if none exists
            # This shouldn't normally be needed as registration creates a personal org
            try:
                org_id = create_organization(token, endpoint)
                print(f"   ✓ Created organization: {org_id}")

                # Set it as the current organization
                if set_current_organization(token, org_id, endpoint):
                    print("   ✓ Current organization set")
            except Exception as create_err:
                print(f"   ❌ Failed to create organization: {create_err}")
                raise Exception(f"Could not get or create organization: {e}") from e

        # Create a new STEAR group for the agent
        print("📦 Creating new STEAR group...")
        try:
            timestamp = int(time.time())
            stear_group_id, registration_secret = create_stear_group(
                token,
                endpoint,
                name=f"SDK Agent STEAR {timestamp}",
                description="STEAR group created by SDK for new agent",
                organization_id=org_id,
            )
            print(f"   ✓ Created new STEAR group: {stear_group_id}")
        except Exception as e:
            print(f"   ❌ Failed to create STEAR group: {e}")
            raise

        # Create agent
        print("🤖 Creating agent...")
        timestamp = int(time.time())
        agent_id, agent_secret = create_agent(
            token,
            stear_group_id,
            endpoint,
            name=f"SDK Demo Agent {timestamp}",
            description="Agent created by SDK with generalized setup",
            organization_id=org_id,
        )
        print(f"   ✓ Agent created: {agent_id}")

        # Save to environment file if requested
        if save_to_env:
            try:
                # Read existing env file if it exists
                env_vars = {}
                if os.path.exists(env_file):
                    try:
                        with open(env_file) as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith("#") and "=" in line:
                                    key, value = line.split("=", 1)
                                    env_vars[key] = value
                    except PermissionError:
                        print(
                            f"   ⚠️  Could not read existing {env_file} (permission denied)"
                        )
                        env_vars = {}

                # Update with new credentials
                env_vars["CERTIV_AGENT_ID"] = agent_id
                env_vars["CERTIV_AGENT_SECRET"] = agent_secret
                env_vars["CERTIV_STEAR_ID"] = stear_group_id
                env_vars["CERTIV_STEAR_SECRET"] = registration_secret

                # Write back to env file
                with open(env_file, "w") as f:
                    for key, value in env_vars.items():
                        f.write(f"{key}={value}\n")

                print(f"✅ Agent credentials saved to {env_file}")
                print("   Next time you can run without --create-agent")

            except PermissionError:
                print(f"⚠️  Could not save to {env_file} (permission denied)")
                print("   Credentials are available for this session only")
                print("   You may need to manually add these to your .env file:")
                print(f"   CERTIV_AGENT_ID={agent_id}")
                print(f"   CERTIV_AGENT_SECRET={agent_secret}")
                print(f"   CERTIV_STEAR_ID={stear_group_id}")
                print(f"   CERTIV_STEAR_SECRET={registration_secret}")
            except Exception as e:
                print(f"⚠️  Could not save to {env_file}: {e}")
                print("   Credentials are available for this session only")

        return agent_id, agent_secret, stear_group_id

    except Exception as e:
        print(f"❌ Failed to setup agent credentials: {e}")
        raise


def create_agent(
    token: str,
    stear_group_id: str,
    endpoint: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    organization_id: Optional[str] = None,
) -> tuple[str, str]:
    """Create an agent and return agent_id and agent_secret

    Args:
        token: Admin authentication token
        stear_group_id: STEAR group ID to associate with the agent
        name: Name for the agent (will be auto-generated if not provided)
        description: Description for the agent

    Returns:
        Tuple of (agent_id, agent_secret)
    """
    import time

    import requests

    if name is None:
        name = f"SDK Demo Agent {int(time.time())}"

    if description is None:
        description = "Agent created by SDK for testing"

    payload = {
        "name": name,
        "description": description,
        "stear_group_id": stear_group_id,
        "metadata": {},
    }

    # Add organization_id if provided
    if organization_id:
        payload["organization_id"] = organization_id

    response = requests.post(
        f"{endpoint}/agent-mgmt",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to create agent: {response.text}")

    data = response.json()
    agent_id = data["agent"]["agent_id"]
    agent_secret = data["agent_secret"]

    logger.info(f"Created agent: {agent_id}")
    return agent_id, agent_secret


def enable_function_patching(function_names: list[str], endpoint: str) -> bool:
    """Enable function patching (secure runtime) for specified functions via agent-mgmt API.

    Args:
        function_names: List of function names to enable secure runtime for
        endpoint: Backend endpoint URL

    Returns:
        True if all functions were successfully patched, False otherwise
    """
    from urllib.parse import quote

    # Get authentication token
    try:
        username = os.getenv("ADMIN_USERNAME", "magos-test")
        password = os.getenv("ADMIN_PASSWORD", "magosmagos1")
        token, _ = login_admin(username, password, endpoint, auto_register=True)
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"❌ Failed to authenticate for patching: {e}")
        return False

    # Get agent ID from environment
    agent_id = os.getenv("CERTIV_AGENT_ID")
    if not agent_id:
        print("❌ Agent ID not found in environment (CERTIV_AGENT_ID)")
        return False

    # Build function signatures with parameters
    function_signatures = {}
    for func_name in function_names:
        # For search_wikipedia, build the signature
        if func_name == "search_wikipedia":
            function_signatures[func_name] = "search_wikipedia(query, sentences)"
        else:
            function_signatures[func_name] = func_name

    success_count = 0
    for function_name in function_names:
        try:
            # Use the full signature with parameters
            full_signature = function_signatures.get(function_name, function_name)
            # URL encode the function signature
            encoded_signature = quote(full_signature, safe="")

            # Use the agent-mgmt endpoint for secure runtime (same as UI)
            import requests

            response = requests.put(
                f"{endpoint}/agent-mgmt/{agent_id}/functions/{encoded_signature}/secure-runtime",
                headers=headers,
                json={
                    "secure_runtime": True,
                    "reason": f"STEAR secure runtime enabled for {function_name} function calls",
                },
                timeout=10,
            )
            if response.status_code == 200:
                print(f"✅ Secure runtime enabled for: {full_signature}")
                success_count += 1
            else:
                print(
                    f"❌ Failed to enable secure runtime for {full_signature}: {response.status_code}"
                )
                if response.text:
                    print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error enabling secure runtime for {function_name}: {e}")

    return success_count == len(function_names)


def disable_function_patching(function_names: list[str], endpoint: str) -> bool:
    """Disable function patching (secure runtime) for specified functions via agent-mgmt API.

    Args:
        function_names: List of function names to disable secure runtime for
        endpoint: Backend endpoint URL

    Returns:
        True if all functions were successfully unpatched, False otherwise
    """
    from urllib.parse import quote

    # Get authentication token
    try:
        username = os.getenv("ADMIN_USERNAME", "magos-test")
        password = os.getenv("ADMIN_PASSWORD", "magosmagos1")
        token, _ = login_admin(username, password, endpoint, auto_register=True)
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"❌ Failed to authenticate for patching cleanup: {e}")
        return False

    # Get agent ID from environment
    agent_id = os.getenv("CERTIV_AGENT_ID")
    if not agent_id:
        print("❌ Agent ID not found in environment (CERTIV_AGENT_ID)")
        return False

    # Build function signatures with parameters
    function_signatures = {}
    for func_name in function_names:
        # For search_wikipedia, build the signature
        if func_name == "search_wikipedia":
            function_signatures[func_name] = "search_wikipedia(query, sentences)"
        else:
            function_signatures[func_name] = func_name

    success_count = 0
    for function_name in function_names:
        try:
            # Use the full signature with parameters
            full_signature = function_signatures.get(function_name, function_name)
            # URL encode the function signature
            encoded_signature = quote(full_signature, safe="")

            # Use DELETE to completely remove the agent-level override
            import requests

            response = requests.delete(
                f"{endpoint}/agent-mgmt/{agent_id}/functions/{encoded_signature}/secure-runtime",
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200 or response.status_code == 204:
                print(f"🔒 Removed secure runtime override for: {full_signature}")
                success_count += 1
            else:
                print(
                    f"❌ Failed to remove secure runtime for {full_signature}: {response.status_code}"
                )
                if response.text:
                    print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error disabling secure runtime for {function_name}: {e}")

    return success_count == len(function_names)
