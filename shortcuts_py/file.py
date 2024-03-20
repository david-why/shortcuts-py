from typing import Any

__all__ = ['StaticFile', 'on_my_ipad']


class StaticFile:
    __shortcuts_is_file__ = True

    def __init__(
        self,
        location_type: str,
        file_provider_domain_id: str,
        subpath: str,
        filename: str,
        display_name: str,
        *,
        app_bundle_id: str | None = None,
    ) -> None:
        self.location_type = location_type
        self.file_provider_domain_id = file_provider_domain_id
        self.subpath = subpath
        self.filename = filename
        self.display_name = display_name
        self.app_bundle_id = app_bundle_id

    def dump(self) -> dict[str, Any]:
        data = {
            'fileLocation': {
                'relativeSubpath': self.subpath,
                'fileProviderDomainID': self.file_provider_domain_id,
                'WFFileLocationType': self.location_type,
            },
            'filename': self.filename,
            'displayName': self.display_name,
        }
        if self.app_bundle_id:
            data['fileLocation']['appContainerBundleIdentifier'] = self.app_bundle_id
        return data

    @staticmethod
    def app_root(app_bundle_id: str, display_name: str = 'Documents'):
        return StaticFile(
            'LocalStorage',
            'com.apple.FileProvider.LocalStorage',
            '',
            'Documents',
            display_name,
            app_bundle_id=app_bundle_id,
        )


on_my_ipad = StaticFile(
    'LocalStorage',
    'com.apple.FileProvider.LocalStorage',
    '',
    'File Provider Storage',
    'On My iPad',
)
