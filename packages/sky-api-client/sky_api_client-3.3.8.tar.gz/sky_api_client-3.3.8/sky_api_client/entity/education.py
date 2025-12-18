from typing import Dict

import six
import re
from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry
from sky_api_client.exceptions.exception import MethodNotDefined
from urllib.parse import quote_plus


def slugify_underscore(name):
    """Return slug for the given name i.e. replace any non alphanumeric character with underscore."""
    if name is None or not isinstance(name, six.text_type):
        return None

    name = name.strip().lower()
    # Any non word characters (letters, digits, and underscores) are replaced by '-'
    name = re.sub(r'\W+', '_', name)
    # Removing any trailing or leading dash
    name = re.sub(r'^[-_]|[-_]$', '', name)
    # Replace multiple continuous hipens with one
    name = re.sub('[-_]+', '_', name)
    return name


@EntityRegistry.register('education')
class Education(Entity):
    LIST_URL = '/constituent/v1/educations/'
    CREATE_URL = '/constituent/v1/educations/'
    GET_URL = '/constituent/v1/constituents/educations/{id}'
    UPDATE_URL = '/constituent/v1/educations/{id}'
    DELETE_URL = '/constituent/v1/educations/{id}'
    SUBJECTS_URL = '/constituent/v1/educations/subjects'
    DEGREES_URL = '/constituent/v1/educations/degrees'

    def add_custom_field_entries(self, education_id, data):
        sky_api_ed_client = EducationCustomField(self._api)
        already_present = {}
        for entry in sky_api_ed_client.custom_fields(education_id):
            ed_custom_field_slug = slugify_underscore(entry['category'])
            if ed_custom_field_slug in data:
                if entry['value'] in (data.get(ed_custom_field_slug) or []):
                    already_present.setdefault(ed_custom_field_slug, [])
                    already_present[ed_custom_field_slug].append(entry['value'])
                else:
                    sky_api_ed_client.delete(entry['id'], parent_id=education_id)

        ed_custom_fields_names = [field['name'] for field in sky_api_ed_client.list(id=education_id)['value']]
        for ed_custom_field in ed_custom_fields_names:
            ed_custom_field_slug = slugify_underscore(ed_custom_field)
            for value in data.get(ed_custom_field_slug) or []:
                if value not in already_present.get(ed_custom_field_slug, []):
                    sky_api_ed_client.create(
                        {
                            'value': value,
                            'category': ed_custom_field,
                            'parent_id': education_id,
                        }
                    )

    def subjects(self):
        if self.SUBJECTS_URL:
            return self._api.request(method='GET', path=self.SUBJECTS_URL).get('value', [])
        raise MethodNotDefined('subjects')

    def degrees(self):
        if self.DEGREES_URL:
            return self._api.request(method='GET', path=self.DEGREES_URL).get('value', [])
        raise MethodNotDefined('degrees')

    def create(self, data: Dict[str, str], id=''):
        response = super().create(data=data, id=id)
        if isinstance(response, dict) and response.get('id'):
            self.add_custom_field_entries(response['id'], data)
        return response

    def update(self, id: str, data: Dict[str, str], parent_id=''):
        response = super().update(id=id, data=data, parent_id=parent_id)
        self.add_custom_field_entries(id, data)
        return response


@EntityRegistry.register('education_custom_field')
class EducationCustomField(Entity):
    LIST_URL = 'constituent/v1/educations/customfields/categories/details?limit=5000'
    CREATE_URL = 'constituent/v1/educations/customfields'
    DELETE_URL = 'constituent/v1/educations/customfields/{id}'
    UPDATE_URL = 'constituent/v1/educations/customfields/{id}'
    CUSTOM_FIELDS_URL = 'constituent/v1/educations/{education_id}/customfields'
    CUSTOM_FIELD_CATEGORIES_CODE_TABLE_URL = 'constituent/v1/educations/customfields/categories/values?category_name={}'

    def list(self, id=None, parent_id=None, params=None, all=False):
        data = super().list(id=id, parent_id=parent_id, params=params)
        if not all:
            return data
        count = data['count']
        while count > 5000:
            params['offset'] = params.get('offset', 0) + 5000
            data['value'] += super().list(id=id, parent_id=parent_id, params=params)['value']
            count -= 5000
        return data

    def custom_fields(self, education_id):
        if self.CUSTOM_FIELDS_URL:
            return self._api.request(method='GET', path=self.CUSTOM_FIELDS_URL.format(education_id=education_id)).get(
                'value', []
            )
        raise MethodNotDefined('custom_fields')

    def custom_field_categories_code_table(self, category_name):
        if self.CUSTOM_FIELD_CATEGORIES_CODE_TABLE_URL:
            return self._api.request(
                method='GET', path=self.CUSTOM_FIELD_CATEGORIES_CODE_TABLE_URL.format(quote_plus(category_name))
            ).get('value', [])
        raise MethodNotDefined('custom_field_categories_code_table')
