import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service class for uploading files to Cloudinary.
    """
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Constructor for the UploadFileService class.

        Args:
            cloud_name (str): the name of the Cloudinary cloud.
            api_key (str): the API key for the Cloudinary cloud.
            api_secret (str): the API secret for the Cloudinary cloud.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Uploads a file to Cloudinary with a specified public ID based on username.

        Args:
            file (UploadFile): The file to be uploaded.
            username (str): The username to use in constructing the public ID.

        Returns:
            str: The URL of the uploaded image.
        """

        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
