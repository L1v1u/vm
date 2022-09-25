import factory
from vm.models import User


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    password = "stringString2"

    class Meta:
        model = User
