from oscar.apps.search.search_indexes import ProductIndex as CoreProductIndex
from haystack import indexes


class ProductIndex(CoreProductIndex):
    conf_items = indexes.MultiValueField(null=True, faceted=True)
    spe = indexes.MultiValueField(null=True, faceted=True)

    def prepare_conf_items(self, obj):
        if not obj.conf:
            return []
        return [item.number for item in obj.conf.items.all()]

    def prepare_spe(self, obj):
        if not obj.conf:
            return
        return [spe.name for spe in obj.conf.specialities.all()]
