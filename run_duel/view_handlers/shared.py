
from tournament.models import Tournament

CURRENT_TOURNAMENT = 3


# Get all duels' information
# for a given tournament
def tournament_all_duels(tournament_id):
    tournament = Tournament.by_id(tournament_id)
    # Empty info if tournament doesn't exist
    if tournament is None:
        return {}
    tournament_info = {
        "tournament": tournament.dictionary(),
        "stages": []
    }
    # Get all stages for tournament
    # then their info
    stages = tournament.all_stages()
    for stage in stages:
        stage_info = {
            "stage": stage.dictionary(),
            "groups": []
        }
        # Get groups, info for each group for this stage
        groups = stage.all_groups()
        for group in groups:
            group_info = {
                "group": group.dictionary(),
                "duels": []
            }
            # Get duels, all info for duels for this group
            duels = group.all_duels()
            for duel in duels:
                # Add duel info to duels array in group
                group_info["duels"].append(
                    duel.dictionary()
                )
            # Now we have all group info
            # push this to stage's groups array
            stage_info["groups"].append(
                group_info
            )
        # Now we have all stage info
        # push to tournament's stages array
        tournament_info["stages"].append(stage)
    return tournament_info


# Remove finished duels
# from tournament all duels info
def remove_finished_duels(tournament_information):
    if "stages" not in tournament_information.keys():
        return {}
    for stage in tournament_information["stages"]:
        for group in stage["groups"]:
            group["duels"] = [
                x for x in group["duels"] if x["status"] != "FINISHED"
            ]
    return tournament_information


#
# Authorisation helper functions
#

# Can a user start duels?
def can_start_duels(request):
    return request.user.groups.filter(name="umpire").exists()


# Can a user decide scores?
def can_record_score(request):
    return request.user.groups.filter(name="umpire").exists()


# Can a user administer duels all powerfully?
def can_administer_duels_all(request):
    return request.user.groups.filter(name="duel_administrator").exists()
