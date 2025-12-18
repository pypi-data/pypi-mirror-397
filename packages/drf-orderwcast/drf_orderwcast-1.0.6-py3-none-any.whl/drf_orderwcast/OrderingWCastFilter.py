from rest_framework.filters import OrderingFilter


class OrderingWCastFilter(OrderingFilter):
    '''
    Use this class to add support for using functions in fields that will be
    sorted.
    If 'ordering_cast' is set in view, use that functions to do the sorting of
    the fields.
    '''

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            ordering_cast = getattr(view, 'ordering_cast', None)
            if ordering_cast:
                cast_ordering = []
                for term in ordering:
                    if term.startswith("-"):
                        field = term[1:]
                        asc = False
                    else:
                        field = term
                        asc = True

                    if field in ordering_cast:
                        cast_term = ordering_cast[field]
                        method_call = cast_term.asc() if asc else cast_term.desc()
                        cast_ordering.append(method_call)
                        continue
                    cast_ordering.append(term)

                ordering = cast_ordering
            return queryset.order_by(*ordering)

        return queryset
