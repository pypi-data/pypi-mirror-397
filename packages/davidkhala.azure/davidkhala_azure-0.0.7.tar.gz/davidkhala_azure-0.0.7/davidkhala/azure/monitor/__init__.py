from dataclasses import dataclass


@dataclass
class AbstractResource:
    immutable_id: str | None
    id: str
    location: str
    name: str
    resource_group_name: str

    def from_resource(self, resource):
        self.id = resource.id
        self.location = resource.location
        self.resource_group_name = resource.id.split('/')[4]
        self.name = resource.name
        if hasattr(resource, 'immutable_id'):
            self.immutable_id = resource.immutable_id
