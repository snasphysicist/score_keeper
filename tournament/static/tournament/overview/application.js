
var vueApplication = new Vue({
  el: '#vue',
  data: {
    tournament: {},
    selectedstage: 0,
    selectedgroup: 0
  },
  computed: {
    groups: function() {
      // Filter down to selected stage
      let stages = this.tournament["stages"].filter(
        stage => (stage["stage"]["number"] == this.selectedstage)
      );
      if (stages.length != 0) {
        return [];
      }
      return stages[0]["groups"];
    },
    selectedGroupId: function() {
      // Filter down to selected stage
      let stage = this.stages.filter(function(stage) {
        return stage["stage"]["number"] == this.selectedstage;
      })
      if (stage.length != 0) {
        return null;
      }
      groups = stage[0]["groups"];
      // Filter down to selected group
      let group = groups.filter(function(group) {
        return group["number"] == this.selectedgroup;
      })
      if (group.length != 0) {
        return null;
      }
      return group[0]["id"];
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

function fetchDuelList() {
  const TOURNAMENT_ID = 3;
  const GET_URL = "/run_duel/api/v1/<0>/duel/list";
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
    if(json["success"]) {
      vueApplication.tournament = json;
    } else {
      // Handle error
    }
  })
}

fetchDuelList();
