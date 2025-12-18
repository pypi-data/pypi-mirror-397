# drf-orderwcast

OrderingFilter subclass that applies functions before sorting the declared
fields.

## Installing

1. `pip install drf-orderwcast`;

2. Add `drf_orderwcast` in INSTALLED_APPS of ``settings.py`` file.

## Using

Use inplace of OrderingFilter in views. Needs to tell the functions in a
dictionary of field name and database functions.

## views.py

```python

from django.db.models.functions import Lower

from drf_orderwcast import OrderingWCastFilter


class FooListView(generics.ListAPIView):
    queryset = Foo.objects.all()
    serializer_class = FooSerializer
    filter_backends = (OrderingWCastFilter,)
    ordering_fields = ['name', 'email']
    ordering_cast = {'name': Lower('name')}

```

In the example above, the `name` field included in `ordering_cast` property
will now have case-consistent ordering. `email` continues to be sorted as it
would be when using the standard `OrderingFilter` class from filters module.
