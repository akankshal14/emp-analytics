from backend.exceptions import (
    ValidationException,
    NotFoundException
)

from backend.repositories.project_repository import (
    ProjectRepository
)

from backend.utils.logger import get_logger
from backend.utils.validators import validate_required


logger = get_logger(__name__)


class ProjectService:

    def __init__(self):

        self.repository = ProjectRepository()

    def get_all_projects(self):

        try:

            return self.repository.get_all()

        except Exception:

            logger.exception(
                "Failed to get projects."
            )

            raise

    def get_project(self, project_id):

        try:

            project = (
                self.repository
                .get_by_id(project_id)
            )

            if not project:

                raise NotFoundException(
                    f"Project {project_id} not found."
                )

            return project

        except Exception:

            logger.exception(
                "Failed to get project."
            )

            raise

    def create_project(
        self,
        project
    ):

        try:

            validate_required(
                project.project_name,
                "Project name"
            )

            validate_required(
                project.start_date,
                "Project start date"
            )

            return self.repository.create(
                project
            )

        except Exception:

            logger.exception(
                "Failed to create project."
            )

            raise

    def update_project(
        self,
        project_id,
        data
    ):

        try:

            existing = (
                self.repository
                .get_by_id(project_id)
            )

            if not existing:

                raise NotFoundException(
                    "Project not found."
                )

            validate_required(
                data["project_name"],
                "Project name"
            )

            return self.repository.update(
                project_id,
                data
            )

        except Exception:

            logger.exception(
                "Failed to update project."
            )

            raise

    def delete_project(
        self,
        project_id
    ):

        try:

            existing = (
                self.repository
                .get_by_id(project_id)
            )

            if not existing:

                raise NotFoundException(
                    "Project not found."
                )

            return self.repository.delete(
                project_id
            )

        except Exception:

            logger.exception(
                "Failed to delete project."
            )

            raise