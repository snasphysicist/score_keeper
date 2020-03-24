
var vueApplication = new Vue({
  el: '#vue',
  data: {
    duels: [],
    participants: [],
    stages: [],
    selectedstage: 0,
    selectedgroup: 0
  },
  computed: {
    groups: function() {
      let groups = [];
      if (this.selectedstage == 0) {
        return groups;
      }
      for (let i = 0; i < this.stages.length; i++) {
        if (this.stages[i]["number"] == this.selectedstage) {
          groups = this.stages[i]["groups"];
          break;
        }
      }
      return groups;
    },
    selectedGroupId: function() {
      let groupNumber = this.selectedgroup;
      for (let i = 0; i < this.groups.length; i++) {
        if (this.groups[i]["number"] == groupNumber) {
          return this.groups[i]["id"];
        }
      }
      return null;
    },
    sortedParticipants: function() {
      let array = this.participants;
      array.sort(
        (a, b) => {
          return (
            -1 * (1000 * (a.completed - b.completed))
            - (a.remaining - b.remaining)
          );
        }
      );
      return array;
    }
  }
});

function getTournamentStagesGroups() {
  const TOURNAMENT_ID = CURRENT_TOURNAMENT;
  const GET_URL = "/tournament/api/v1/<0>/stagesgroups";
  // Insert ID into url
  let url = GET_URL.replace(
    "<0>",
    TOURNAMENT_ID
  );
  fetch(
    url,
    {
      method: "GET",
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if (json["success"]) {
      vueApplication.stages = json["stages"];
    }
  })
}

getTournamentStagesGroups();

function getDuelsForGroup() {
  let groupId = vueApplication.selectedGroupId;
  // Exit if group id invalid
  if (groupId == null) {
    return;
  }
  const GET_URL = "/tournament/api/v1/<0>/overview";
  // Insert ID into url
  let url = GET_URL.replace(
    "<0>",
    groupId
  );
  fetch(
    url,
    {
      method: "GET",
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if (json["success"]) {
      vueApplication.duels = json["duels"];
      vueApplication.participants = json["participants"];
    }
  })
}
