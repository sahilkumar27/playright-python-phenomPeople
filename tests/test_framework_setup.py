import pytest


# @pytest.mark.smoke
def test_phenom_application_launch(application):

    print("Phenom application launched successfully")

    print("Current URL:", application.url)

    print("Page Title:", application.title())