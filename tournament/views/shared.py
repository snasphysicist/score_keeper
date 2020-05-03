

# Can a user start duels?
def can_administer_duels(request):
    return request.user.groups.filter(name="duel_administrator").exists()
