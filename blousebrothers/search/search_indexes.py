from oscar.apps.search.search_indexes import ProductIndex as CoreProductIndex
from haystack import indexes


class ProductIndex(CoreProductIndex):
    """
    When ProductIndex is modifed, you need to update solr schema.xml by running :

    $> ./manage.py build_solr_schema

    Then you need to sync compose/solr/solr_cfg/mycore/conf/schema.xml with new output.
    But just add the new items, not all the differences !
    In fact you can only just edit existing schema. And then rebuild index :

    $> ./manage.py rebuild_index --noinput
    """
    conf_items = indexes.MultiValueField(null=True, faceted=True)
    spe = indexes.MultiValueField(null=True, faceted=True)
    owner = indexes.CharField(model_attr="conf__owner__username")

    def prepare_conf_items(self, obj):
        if not obj.conf:
            return []
        return [item.number for item in obj.conf.items.all()]

    def prepare_spe(self, obj):
        if not obj.conf:
            return
        return [spe.name for spe in obj.conf.specialities.all()]

    def prepare(self, obj):
        prepared_data = super(ProductIndex, self).prepare(obj)

        # Use title to for spelling suggestions
        prepared_data['suggestions'] = prepared_data['title']

        return prepared_data
