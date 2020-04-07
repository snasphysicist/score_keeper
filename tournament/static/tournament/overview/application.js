
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
      if (stages.length != 1) {
        return [];
      }
      return stages[0]["groups"];
    },
    group: function() {
      let groups = this.groups.filter(
        group => (group["group"]["number"] == this.selectedgroup)
      );
      if (groups.length != 1) {
        return {duels: []};
      }
      return group[0];
    },
    participants: function() {
      if (this.group["duels"].length == 0) {
        return [];
      }
      // Get unique participants in group
      let uniqueParticipants = [];
      this.group["duels"].forEach(
        duel => {
          let added = participants.map(
            participant => participant["id"]
          );
          if (
            added.indexOf(
              duel["opponent1"]["id"]
            ) > -1
          ) {
            participants.push(duel["opponent1"]);
          }
          if (
            added.indexOf(
              duel["opponent2"]["id"]
            ) > -1
          ) {
            participants.push(duel["opponent2"]);
          }
        }
      );
      return uniqueParticipants;
    },
    participantsWithScore: function() {
      if (this.participants.length == 0) {
        return [];
      }
      let participantsFull = this.participants;
      participantsFull.forEach(
        participant => {
          // Add up scores when participant is opponent 1
          let score = this.group["duels"].filter(
            // Get only duels where participant is opponent 1
            duel => duel["opponent1"]["id"] == participant["id"];
          ).map(
            // Extract opponent 1 score
            duel => duel["score"]["opponent1"]
          ).reduce(
            // Sum scores
            (accumulator, value) => accumulator + value;
          );
          // Add scores where participant is opponent 2
          score += this.group["duels"].filter(
            duel => duel["opponent2"]["id"] == participant["id"];
          ).map(
            duel => duel["score"]["opponent2"]
          ).reduce(
            // Sum scores
            (accumulator, value) => accumulator + value;
          );
          // Add summed score to participant object
          participant["score"] = score;
        }
      );
      return participantsFull;
    },
    sortedParticipants: function() {
      let array = this.participantsWithScore;
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
