from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse
from users.decorators import login_required
from drumbeat import messages

from activity.models import Activity


def index(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    if activity.deleted:
        messages.error(request, _('This message was deleted.'))
        if activity.can_edit(request.user):
            return HttpResponseRedirect(reverse('activity_restore',
                kwargs={'activity_id': activity.id}))
        elif activity.target_project:
            return HttpResponseRedirect(activity.target_project.get_absolute_url())
        else:
            return HttpResponseRedirect(activity.actor.get_absolute_url())
    return render_to_response('activity/index.html', {
        'activity': activity,
    }, context_instance=RequestContext(request))


@login_required
def delete_restore(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    if not activity.can_edit(request.user):
        return HttpResponseForbidden(_("You can't edit this message"))
    if request.method == 'POST':
        activity.deleted = not activity.deleted
        activity.save()
        msg = _('Message deleted!') if activity.deleted else _('Message restored!')
        messages.success(request, msg)
        if activity.target_project:
            return HttpResponseRedirect(activity.target_project.get_absolute_url())
        else:
            return HttpResponseRedirect(reverse('dashboard_index'))
    else:
        return render_to_response('activity/delete_restore.html', {
            'activity': activity,
        }, context_instance=RequestContext(request))
