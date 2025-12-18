# tests/test_generator.py
import os
from scaffold.generator import create_project

def test_create_basic_project(tmp_path):
    """
    GIVEN a temporary directory (tmp_path)
    WHEN the create_project function is called with the 'basic' template
    THEN it should create the correct directory structure and files
    """
    project_name = "test_project"
    template_name = "basic"

    # Run our generator function, telling it to create the project
    # inside the temporary directory provided by pytest
    create_project(project_name, template_name=template_name, target_dir=tmp_path)

    # Define the paths we expect to exist
    project_dir = tmp_path / project_name
    src_dir = project_dir / "src" / "test_project"
    
    # Use assertions to check if the directories were created
    assert project_dir.is_dir()
    assert src_dir.is_dir()

    # Use assertions to check if the files were created
    assert (project_dir / "pyproject.toml").is_file()
    assert (project_dir / "README.md").is_file()
    assert (project_dir / ".gitignore").is_file()
    assert (src_dir / "main.py").is_file()
    assert (src_dir / "__init__.py").is_file()

def test_create_fastapi_project(tmp_path):
    """
    GIVEN a temporary directory
    WHEN the create_project function is called with the 'fastapi' template
    THEN it should create the correct structure and include FastAPI dependencies
    """
    project_name = "test_api_project"
    template_name = "fastapi"

    create_project(project_name, template_name=template_name, target_dir=tmp_path)

    project_dir = tmp_path / project_name
    pyproject_path = project_dir / "pyproject.toml"

    # Check that the main file was created
    assert (project_dir / "src" / "test_api_project" / "main.py").is_file()

    # Check that the pyproject.toml contains the word "fastapi"
    # This is a simple way to verify the correct template was used
    pyproject_content = pyproject_path.read_text()
    assert "fastapi" in pyproject_content