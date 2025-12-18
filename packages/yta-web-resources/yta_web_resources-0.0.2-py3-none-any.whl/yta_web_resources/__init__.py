"""
Our module to generate web resources dynamically to
be able to download them later with a scrapper to be
used in the video edition.

A web resource is a web page that we built with the
intention of being able to download elements (images)
from it by scraping with a web scraper.

Each resource web page is included in the project, but
also can have a remote url to be used, and a Google
Drive url to download it locally. So, it can be used
locally from the internal file, from the one downloaded
locally from Google Drive, or remotely (if the remote
url is available).
"""
from yta_web_scraper.chrome import ChromeScraper
from yta_general_utils.url.dataclasses import UrlParameters, UrlParameter
from yta_validation.parameter import ParameterValidator
from yta_programming_path import DevPathHandler
from yta_programming.var import CaseStyleHandler
from yta_file.handler import FileHandler
from yta_file_downloader import Downloader
from typing import Union


# TODO: Use this or remove it
_WAITING_TIME: float = 0.1
"""
*For internal use only*

The time the scraper will wait when some 'wait'
process must be done (in order to detect if a 
component is visible or similar).
"""

class _WebResource:
    """
    *For internal use only*

    Base class to include the information about a web
    resource.
    """

    @property
    def filename(
        self
    ) -> str:
        """
        The filename, but based on the name of this class, that
        will be unique.
        
        If the class is 'BookingReviewImage', the filename will
        be 'booking_review_image.html' (notice that the '.html'
        extension will be added).
        """
        return f'{CaseStyleHandler.upper_camel_case_to_snake_case(self.__class__.__name__)}.html'
    
    @property
    def url(
        self
    ) -> str:
        """
        The url that must be used to interact with the
        web page that is able to catch the audio and to
        transcribe it.
        """
        return (
            self.get_local_url(None)
            # TODO: Use a mode instead
            if self.do_use_local_url else
            self.get_remote_url(None)
        )

    def __init__(
        self,
        local_path: str,
        google_drive_direct_download_url: str,
        remote_url: Union[str, None] = None,
        # TODO: Do I need this here? maybe a mode is better (?)
        do_use_local_url: bool = True,
        do_use_gui: bool = False
    ):
        self.local_path: str = local_path
        """
        The local path of the web resource that we include in
        this project.
        
        It has to be something like:
        'web/booking/index.html'
        """
        self.google_drive_direct_download_url: str = google_drive_direct_download_url
        """
        The Google Drive direct download url to obtain the file
        and download it to use locally.

        It has to be something like:
        'https://drive.google.com/file/d/1TyAz89ZLIMB3a-fk1qaaKa2qDoVHJ8t3/view?usp=sharing'
        """
        self.remote_url: Union[str, None] = remote_url
        """
        The remote url, if existing, we can access to obtain the
        resource by scraping it.
        """

        self.scraper: ChromeScraper = ChromeScraper(
            do_use_gui = do_use_gui
        )

        """
        The scraper that will scrape the resource web page and
        download the item.
        """
        self.do_use_local_url: bool = do_use_local_url

        # TODO: This only if the mode is local but downloading
        # if self.do_use_local_url:
        #     # We need to make sure the file exist
        #     self._download_web_file()

        # self._load()

    def _download_web_file(
        self
    ) -> str:
        """
        *For internal use only*

        Download the html file from Google Drive to the specific
        local location, if it has not been downloaded previously
        and is not available.

        This method will return the local file abspath in which
        it is located.
        """
        local_file_abspath = f'{DevPathHandler.get_project_abspath()}{self.filename}'

        if not FileHandler.is_file(local_file_abspath):
            # TODO: We need 'yta_google_drive_downloader' to download it
            # but could we avoid that dependency (?)
            Downloader.download_google_drive_resource(
                self.google_drive_direct_download_url,
                self.filename
            )

        return local_file_abspath

    def get_local_url(
        self,
        parameters: Union[UrlParameters, None]
    ) -> str:
        """
        Get the local url, including the `parameters` provided
        (if provided), but using the file that is included in
        the project.
        """
        ParameterValidator.validate_instance_of('parameters', parameters, UrlParameters)

        # TODO: To open it locally is file:///{abspath}
        # This below is the one we download and use
        #local_downloaded_abspath = f'{DevPathHandler.get_project_abspath()}{self.filename}.html'
        # This below is the one included in the project, not downloaded
        # TODO: We need to call the method that downloads it
        
        local_project_abspath = f'{DevPathHandler.get_project_abspath()}{self.local_path}'
        local_url = f'file:///{local_project_abspath}'

        parameters = (
            ''
            if parameters is None else
            f'?{parameters.encoded}'
        )

        return f'{local_url}{parameters}'
    
    def get_local_downloaded_url(
        self,
        parameters: Union[UrlParameters, None]
    ) -> str:
        """
        Get the local url, including the `parameters` provided
        (if provided), but using the file that is downloaded
        from the Google Drive url.
        """
        # TODO: Download the file if not downloaded yet
        local_downloaded_abspath = self._download_web_file()
        #local_downloaded_abspath = f'{DevPathHandler.get_project_abspath()}{self.filename}.html'
        local_url = f'file:///{local_downloaded_abspath}'

        parameters = (
            ''
            if parameters is None else
            f'?{parameters.encoded}'
        )

        return f'{local_url}{parameters}'
    
    def get_remote_url(
        self,
        parameters: Union[UrlParameters, None]
    ) -> str:
        """
        Get the remote url but including the `parameters` provided.

        This method will raise an exception if the remote url is 
        not available.
        """
        if self.remote_url is None:
            raise Exception('Sorry, no remote url is available.')
        
        ParameterValidator.validate_instance_of(parameters, UrlParameters)

        parameters = (
            ''
            if parameters is None else
            f'?{parameters.encoded}'
        )

        return f'{self.remote_url}{parameters}'
    
    def _get_url(
        self,
        parameters: Union[UrlParameters, None]
    ) -> str:
        """
        *For internal use only*

        Get the url that must be used, including the `parameters`
        provided (if provided).

        # TODO: We still need to implement the 'mode'.
        This method will use the url based on the mode.
        """
        ParameterValidator.validate_instance_of('parameters', parameters, UrlParameters)

        parameters = (
            ''
            if parameters is None else
            f'?{parameters.encoded}'
        )

        return f'{self.url}{parameters}'
    
    # TODO: Implement a method that navigates, do something,
    # and finishes
    def _load(
        self,
        parameters: Union[UrlParameters, None]
    ) -> None:
        """
        *For internal use only*

        Navigates to the web page when not yet on it.
        """
        url = self._get_url(parameters)

        if self.scraper.current_url != url:
            self.scraper.go_to_web_and_wait_until_loaded(url)

    def reload(
        self
    ) -> bool:
        """
        Force a refresh in the web page to reload it.
        """
        # TODO: It was previously like this below:
        # return self.scraper.go_to_web_and_wait_until_loaded(self.url)
        # Force to wait until completely loaded
        return self.scraper.go_to_web_and_wait_until_loaded(self.scraper.current_url)

class BookingReviewImageWebResource(_WebResource):
    """
    Web resource to create a Booking platform review and
    download it as an image.
    """

    def get_booking_review(
        self,
        name: str = 'María',
        country: str = 'México',
        score: str = '9,5',
        score_label: str = 'Exceptional',
        text: str = 'Hotel excelente, muy cómodo y bien ubicado.',
        date: str = 'Estancia de febrero de 2025',
        output_filename: str = 'booking_review.png'
    ) -> str:
        """
        Navigate to the web resource and obtain a Booking Review
        with the parameters provided, that will be stored with
        the `output_filename` filename provided.
        """
        parameters = UrlParameters([
            UrlParameter('name', name),
            UrlParameter('country', country),
            UrlParameter('score', score),
            UrlParameter('scoreLabel', score_label),
            UrlParameter('text', text),
            UrlParameter('date', date)
        ])

        """
        name = 'María'
        country = 'México'
        score = '9,6' # has to be with comma
        scoreLabel = 'Excepcional'
        text = 'Hotel%20excelente%2C%20muy%20cómodo%20y%20bien%20ubicado.'
        date = 'Estancia%20de%20febrero%202025'
        # TODO: Transform the parameters into the query
        parameters = '?name=María%20López&country=México&score=9,6&scoreLabel=Excepcional&text=Hotel%20excelente%2C%20muy%20cómodo%20y%20bien%20ubicado, y un desayuno espectacular.&date=Estancia%20de%20febrero%202025'
        """

        self._load(parameters)

        # TODO: Include this method to get the screenshot
        # with a transaprent background
        self.scraper.driver.execute_cdp_cmd(
            'Emulation.setDefaultBackgroundColorOverride',
            {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}}
        )
        self.scraper.screenshot_element(
            element = self.scraper.find_element_by_id_waiting('review-card'),
            # element = self.scraper.find_element_by_id_waiting('screenshot-wrapper'),
            output_filename = output_filename
        )
        self.scraper.driver.execute_cdp_cmd(
            'Emulation.setDefaultBackgroundColorOverride',
            {}
        )

        return output_filename

# TODO: Maybe we can combine this with the one in
# 'yta-transcriber' and create a class dedicated to
# navigate through webpage resources and use them,
# and the way we use them for each resource is defined
# in the different projects