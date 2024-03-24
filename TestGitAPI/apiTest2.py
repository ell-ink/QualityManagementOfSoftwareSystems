import unittest
from client import GitHubAPIClient, User, Repository
import os
import random
import string


def load_env():
    with open('.env') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            key, value = line.strip().split('=', 1)
            os.environ[key] = value


load_env()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


class TestGitHubAPIClient(unittest.TestCase):
    def setUp(self):
        self.api_client = GitHubAPIClient()

    def tearDown(self):
        pass

    def _generate_random_string(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))

    def _create_unique_repo_name(self):
        return f"test-repo-{self._generate_random_string(6)}"

    def test_get_user(self):
        username = "el-link"
        response = self.api_client.get_user(username)
        self.assertEqual(response.status_code, 200, f"Failed to get user {username}: {response.text}")
        user_data = response.json()
        user = User(**user_data)
        self.assertEqual(user.login, username)

    def test_create_update_delete_repo(self):
        repo_name = self._create_unique_repo_name()
        repo_data = {
            "name": repo_name,
            "private": True
        }

        response = self.api_client.create_repo(GITHUB_TOKEN, repo_data)
        self.assertEqual(response.status_code, 201, f"Failed to create repository: {response.text}")
        repo_data_response = response.json()
        new_repo = Repository(**repo_data_response)
        self.assertEqual(new_repo.name, repo_name)

        updated_repo_name = f"updated-{repo_name}"
        update_data = {
            "name": updated_repo_name,
            "private": False
        }
        response = self.api_client.update_repo(GITHUB_TOKEN, new_repo.owner.login, new_repo.name, update_data)
        self.assertEqual(response.status_code, 200, f"Failed to update repository: {response.text}")
        updated_repo_data = response.json()
        updated_repo = Repository(**updated_repo_data)
        self.assertEqual(updated_repo.name, updated_repo_name)

        response = self.api_client.delete_repo(GITHUB_TOKEN, updated_repo.owner.login, updated_repo.name)
        self.assertEqual(response.status_code, 204, f"Failed to delete repository: {response.text}")

    def test_get_user_repositories(self):
        username = "el-link"
        response = self.api_client.get_user_repositories(username)
        self.assertEqual(response.status_code, 200, f"Failed to get repositories for user {username}: {response.text}")
        repositories = response.json()
        self.assertTrue(isinstance(repositories, list))


if __name__ == '__main__':
    unittest.main()
