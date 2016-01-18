"""Constants."""

__all__ = [
    "NodeStatus",
]

from twisted.python import constants


def ValueConstant(value, title):
    """Return a `ValueConstant` with a title attribute.

    `ValueConstant` is not meant to be subclassed, but we can add a ``title``
    attribute to an instance.
    """
    constant = constants.ValueConstant(value)
    constant.title = title
    return constant


class NodeStatus(constants.Values):
    """A node's possible statuses.

    These are copied from MAAS's source code. Some statuses are no longer
    used.
    """

    # The node has been created and has a system ID assigned to it.
    NEW = ValueConstant(0, "New")
    # Testing and other commissioning steps are taking place.
    COMMISSIONING = ValueConstant(1, "Commissioning")
    # The commissioning step failed.
    FAILED_COMMISSIONING = ValueConstant(2, "Failed commissioning")
    # The node can't be contacted.
    MISSING = ValueConstant(3, "Missing")
    # The node is in the general pool ready to be deployed.
    READY = ValueConstant(4, "Ready")
    # The node is ready for named deployment.
    RESERVED = ValueConstant(5, "Reserved")
    # The node has booted into the operating system of its owner's choice
    # and is ready for use.
    DEPLOYED = ValueConstant(6, "Deployed")
    # The node has been removed from service manually until an admin
    # overrides the retirement.
    RETIRED = ValueConstant(7, "Retired")
    # The node is broken: a step in the node lifecyle failed.
    # More details can be found in the node's event log.
    BROKEN = ValueConstant(8, "Broken")
    # The node is being installed.
    DEPLOYING = ValueConstant(9, "Deploying")
    # The node has been allocated to a user and is ready for deployment.
    ALLOCATED = ValueConstant(10, "Allocated")
    # The deployment of the node failed.
    FAILED_DEPLOYMENT = ValueConstant(11, "Failed deployment")
    # The node is powering down after a release request.
    RELEASING = ValueConstant(12, "Releasing")
    # The releasing of the node failed.
    FAILED_RELEASING = ValueConstant(13, "Releasing failed")
    # The node is erasing its disks.
    DISK_ERASING = ValueConstant(14, "Disk erasing")
    # The node failed to erase its disks.
    FAILED_DISK_ERASING = ValueConstant(15, "Failed disk erasing")
