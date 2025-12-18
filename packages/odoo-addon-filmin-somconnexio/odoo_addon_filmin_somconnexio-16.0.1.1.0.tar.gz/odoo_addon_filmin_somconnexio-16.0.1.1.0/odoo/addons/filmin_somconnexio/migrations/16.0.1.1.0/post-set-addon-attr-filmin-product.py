from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """
    Add product_attribute addon to product_template_attribute_value in filmin_product
    """

    filmin_product = env.ref(
        "filmin_somconnexio.FilminSubscription", raise_if_not_found=False
    )
    if not filmin_product:
        _logger.warning("FilminSubscription not found, skipping update.")
        return

    add_on_attribute_value = env.ref("somconnexio.AddOn", raise_if_not_found=False)
    if not add_on_attribute_value:
        _logger.warning("AddOn attribute value not found, skipping update.")
        return

    template_attr_value_addon = env["product.template.attribute.value"].search(
        [
            ("product_tmpl_id", "=", filmin_product.product_tmpl_id.id),
            ("product_attribute_value_id", "=", add_on_attribute_value.id),
        ]
    )
    if (
        template_attr_value_addon.id
        in filmin_product.product_template_attribute_value_ids.ids
    ):
        _logger.info(
            "FilminSubscription already has AddOn attribute value, skipping update."
        )
        return

    filmin_product.write(
        {"product_template_attribute_value_ids": [(4, template_attr_value_addon.id)]}
    )
    _logger.info("Added AddOn attribute value to FilminSubscription.")
    # Ensure the product is active
    if not filmin_product.active:
        filmin_product.write({"active": True})
        _logger.info("FilminSubscription product unarchived.")
