from blog.models import sendNotif

def add_variable_to_context(request):
    num = 0
    notifs = sendNotif.objects.all()
    try:
        for n in notifs:
            if n.post.author == request.user:
                if n.seen == False:
                    num += 1
    except:
        num = 0

    return {
        'num': num,
}
