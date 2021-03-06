from django.contrib import admin
from django.contrib.admin.utils import reverse_field_path
from django.db.models import Count, Q
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text, smart_text
import string
from choices.models import Talent


def filter_lookups_queryset(request, qs, parameter_name=None, lookup_kwarg=None):
    target_params = ('rating', 'rater__id__exact', 'gender__exact', 'type__exact', 'age_range__exact', 'average_rating',
                     'vendor__id__exact', 'language__id__exact', 'talent__language__id__exact',
                     'talent__vendor__id__exact', 'client__id__exact', 'status__exact', 'talent__gender__exact',
                     'talent__average_rating', 'author__client__id__exact', 'author__id__exact')

    # Filter lookup queryset for all target_params in request.GET params, except for param of request initiator itself
    if lookup_kwarg:
        initial_attrs = dict([(param, val) for param, val in request.GET.iteritems()
                              if param in target_params and val and param != lookup_kwarg])
    else:
        initial_attrs = dict([(param, val) for param, val in request.GET.iteritems()
                              if param in target_params and val and param])
    qs = qs.filter(**initial_attrs)

    if parameter_name != "under_review" and "under_review" in request.GET:
        if request.GET["under_review"] == "0":
            qs = qs.exclude(
                Q(selection__status="REJECTED") |
                Q(selection__status="APPROVED") |
                Q(selection__status="PREAPPROVED")
            )

    if parameter_name != "comment_count" and "comment_count" in request.GET:
        qs = qs.annotate(comment_count=Count('comments'))
        if request.GET["comment_count"] == "0":
            qs = qs.filter(comment_count__lt=1)
        if request.GET["comment_count"] == "1":
            qs = qs.filter(comment_count__gte=1)

    # Filter lookup queryset for each of 3 selection status params, omitting that param if initiated by one of the 3.
    status_params = ('preapproved', 'approved', 'rejected')
    if parameter_name and parameter_name in status_params:
        status_attrs = dict([('selection__status', parameter_name.upper())])
        qs = qs.filter(**status_attrs).annotate(obj_count=Count('pk'))
        extra_status_attrs = [(param, val) for param, val in request.GET.iteritems()
                              if param in status_params and param != parameter_name and val]
    else:
        extra_status_attrs = [(param, val) for param, val in request.GET.iteritems()
                              if param in status_params and val]
    if len(extra_status_attrs) > 0:
        for item in extra_status_attrs:
            qs = qs.filter(id__in=Talent.objects
                           .filter(selection__status=item[0].upper())
                           .annotate(status_count=Count('selection__status'))
                           .filter(status_count=int(int(item[1]))))
    return qs


def filter_lookups_related_queryset(request, qs, lookup_kwarg=None):
    target_params = ['talent__gender__exact', 'talent__language__id__exact', 'client__id__exact',
                     'talent__vendor__id__exact', 'status__exact', 'talent__average_rating']

    initial_attrs = {}

    if lookup_kwarg:
        for param, val in request.GET.iteritems():
            if param in target_params and param != lookup_kwarg and val:
                if param.split('__')[0] == 'client':
                    param = string.replace(param, 'client', 'selection__client')
                elif param.split('__')[0] == 'talent':
                    param = string.replace(param, 'talent', 'selection__talent')
                elif param.split('__')[0] == 'status':
                    param = string.replace(param, 'status', 'selection__status')
                initial_attrs[param] = val
    else:
        for param, val in request.GET.iteritems():
            if param in target_params and val:
                if param.split('__')[0] == 'client':
                    param = string.replace(param, 'client', 'selection__client')
                elif param.split('__')[0] == 'talent':
                    param = string.replace(param, 'talent', 'selection__talent')
                elif param.split('__')[0] == 'status':
                    param = string.replace(param, 'status', 'selection__status')
                initial_attrs[param] = val

    qs = qs.filter(**initial_attrs)

    return qs


class InReviewFilter(admin.SimpleListFilter):
    parameter_name = 'under_review'
    title = 'under review'
    YES, NO = 1, 0

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        queryset = filter_lookups_queryset(request, queryset, parameter_name=self.parameter_name)

        yes_test = queryset.filter(
            Q(selection__status="REJECTED") |
            Q(selection__status="APPROVED") |
            Q(selection__status="PREAPPROVED")
        ).distinct()

        no_test = queryset.exclude(
            Q(selection__status="REJECTED") |
            Q(selection__status="APPROVED") |
            Q(selection__status="PREAPPROVED")
        ).distinct()

        prompts = ()

        if yes_test.count() > 0:
            prompts += ((self.YES, 'yes'),)

        if no_test.count() > 0:
            prompts += ((self.NO, 'no'),)

        return prompts

    def queryset(self, request, queryset):
        queryset = filter_lookups_queryset(request, queryset)
        if self.value() and int(self.value()) == self.YES:
            return queryset.filter(
                Q(selection__status="REJECTED") |
                Q(selection__status="APPROVED") |
                Q(selection__status="PREAPPROVED")
            ).distinct()
        if self.value() and int(self.value()) == self.NO:
            return queryset.exclude(
                Q(selection__status="REJECTED") |
                Q(selection__status="APPROVED") |
                Q(selection__status="PREAPPROVED")
            ).distinct()
        return queryset


class StatusFilter(admin.SimpleListFilter):
    title = ''
    parameter_name = ''

    def lookups(self, request, model_admin):
        qs = filter_lookups_queryset(request, model_admin.get_queryset(request), self.parameter_name)
        tuple_set = ()
        for number in sorted(qs.order_by().values_list('obj_count', flat=True).distinct()):
            tuple_set += ((number, str(number)),)
        return tuple_set

    def queryset(self, request, queryset):
        if self.value():
            qs = self.process_queryset(request, queryset)
            return qs
        else:
            return queryset

    def process_queryset(self, request, queryset):
        if hasattr(queryset[0], 'status_count'):
            qs = queryset.filter(id__in=Talent.objects
                                 .filter(selection__status=self.parameter_name.upper())
                                 .annotate(status_count=Count('selection__status'))
                                 .filter(status_count=int(request.GET[self.parameter_name])))
        else:
            qs = queryset.filter(selection__status=self.parameter_name.upper()).annotate(status_count=Count('pk'))
            qs = qs.filter(status_count=int(request.GET[self.parameter_name]))
        return qs


class PreapprovedFilter(StatusFilter):
    title = 'times preapproved'
    parameter_name = 'preapproved'


class ApprovedFilter(StatusFilter):
    title = 'times accepted'
    parameter_name = 'approved'


class RejectedFilter(StatusFilter):
    title = 'times rejected'
    parameter_name = 'rejected'


class FilteredChoicesFieldListFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__exact' % field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        # Obey parent ModelAdmin queryset when deciding which options to show
        parent_model, reverse_path = reverse_field_path(model, field_path)
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        if field_path == "talent__gender":
            queryset = filter_lookups_related_queryset(request, queryset, lookup_kwarg=self.lookup_kwarg)
        else:
            queryset = filter_lookups_queryset(request, queryset, lookup_kwarg=self.lookup_kwarg)

        self.lookup_choices = (queryset
                               .distinct()
                               .order_by(field.name)
                               .values_list(field.name, flat=True))

        super(FilteredChoicesFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None,
            'query_string': changelist.get_query_string(
                {}, [self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            'display': _('All')
        }
        none_title = ''
        for lookup, title in self.field.flatchoices:
            if lookup is None:
                none_title = title
                continue
            if lookup in self.lookup_choices:
                yield {
                    'selected': smart_text(lookup) == self.lookup_val,
                    'query_string': changelist.get_query_string(
                        {self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]
                    ),
                    'display': title,
                }
        if none_title:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string({
                    self.lookup_kwarg_isnull: 'True',
                }, [self.lookup_kwarg]),
                'display': none_title,
            }
admin.FieldListFilter.register(lambda f: bool(f.choices), FilteredChoicesFieldListFilter)


class FilteredAllValuesFieldListFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        self.empty_value_display = model_admin.get_empty_value_display()
        parent_model, reverse_path = reverse_field_path(model, field_path)
        # Obey parent ModelAdmin queryset when deciding which options to show
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        if self.lookup_kwarg == 'talent__average_rating':
            queryset = filter_lookups_related_queryset(request, queryset, lookup_kwarg=self.lookup_kwarg)
        else:
            queryset = filter_lookups_queryset(request, queryset, lookup_kwarg=self.lookup_kwarg)
        self.lookup_choices = (queryset
                               .distinct()
                               .order_by(field.name)
                               .values_list(field.name, flat=True))
        super(FilteredAllValuesFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None and self.lookup_val_isnull is None,
            'query_string': changelist.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        include_none = False
        for val in self.lookup_choices:
            if val is None:
                include_none = True
                continue
            val = smart_text(val)
            yield {
                'selected': self.lookup_val == val,
                'query_string': changelist.get_query_string({
                    self.lookup_kwarg: val,
                }, [self.lookup_kwarg_isnull]),
                'display': val,
            }
        if include_none:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string({
                    self.lookup_kwarg_isnull: 'True',
                }, [self.lookup_kwarg]),
                'display': self.empty_value_display,
            }
admin.FieldListFilter.register(lambda f: True, FilteredAllValuesFieldListFilter)


class FilteredRelatedOnlyFieldListFilter(admin.RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        queryset = model_admin.get_queryset(request)
        lookup_kwarg = "%s__id__exact" % self.field_path
        queryset = filter_lookups_queryset(request, queryset, lookup_kwarg=lookup_kwarg)
        pk_qs = queryset.distinct().values_list('%s__pk' % self.field_path, flat=True)
        field_choices = field.get_choices(include_blank=False, limit_choices_to={'pk__in': pk_qs})
        return field_choices

    @property
    def include_empty_choice(self):
        """
        Return True if a "(None)" choice should be included, which filters
        out everything except empty relationships.
        """
        return self.field.null or (self.field.is_relation and self.field.many_to_many)\
            or (self.field_path == 'client' and self.field.name == 'client')


class CommentsCountFilter(admin.SimpleListFilter):
    parameter_name = 'comment_count'
    title = 'Has Comments'
    YES, NO = 1, 0

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        queryset = filter_lookups_queryset(request, queryset, parameter_name=self.parameter_name)
        queryset = queryset.annotate(comment_count=Count('comments'))

        yes_test = queryset.filter(comment_count__gte=1)
        no_test = queryset.filter(comment_count__lt=1)

        prompts = ()
        if yes_test.count() > 0:
            prompts += ((self.YES, 'yes'),)

        if no_test.count() > 0:
            prompts += ((self.NO, 'no'),)

        return prompts

    def queryset(self, request, queryset):
        queryset = filter_lookups_queryset(request, queryset, parameter_name=self.parameter_name)
        qs = queryset.annotate(comment_count=Count('comments'))

        if self.value() and int(self.value()) == self.YES:
            return qs.filter(comment_count__gte=1)
        if self.value() and int(self.value()) == self.NO:
            return qs.filter(comment_count__lt=1)

        return queryset
