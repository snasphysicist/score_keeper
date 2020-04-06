let vueApplication = new Vue({
  el: "#vue",
  data: {
    selectedstage: "",
    selectedgroup: "",
    selectedduel: "",
    selectedround: "",
    tournament: {
      "stages": []
    },
    duel: {}
  },
  computed: {
    allStages: function() {
      if (this.tournament["stages"]) {
        return this.tournament["stages"];
      } else {
        return [];
      }
    },
    stageGroups: function() {
      if (!this.tournament["stages"]) {
        return [];
      }
      // Filter down to selected stage
      let selectedStage = this.selectedstage;
      let stage = this.tournament["stages"].filter(function(stage) {
        return stage["stage"]["number"] == selectedStage;
      });
      if (stage.length != 1) {
        return [];
      }
      return stage[0]["groups"];
    },
    groupDuels: function() {
      let groups = this.stageGroups;
      let selectedGroup = this.selectedgroup;
      let group = groups.filter(function(group) {
        return group["group"]["number"] == selectedGroup;
      });
      if (group.length != 1) {
        return [];
      }
      return group[0]["duels"];
    },
    duelRounds: function() {
      let duels = this.groupDuels;
      let selectedDuel = this.selectedduel;
      let duel = duels.filter(function(duel) {
        // Match on two opponent names
        return (
          selectedDuel.includes(
            duel["opponent1"]["battle_name"]
          )
          && selectedDuel.includes(
            duel["opponent2"]["battle_name"]
          )
        );
      });
      if (duel.length != 1) {
        return [];
      }
      return duel[0]["rounds"];
    },
    selectedDuelData: function() {
      let duels = this.groupDuels;
      let selectedDuel = this.selectedduel;
      let duel = duels.filter(function(duel) {
        // Match on two opponent names
        return (
          selectedDuel.includes(
            duel["opponent1"]["battle_name"]
          )
          && selectedDuel.includes(
            duel["opponent2"]["battle_name"]
          )
        );
      });
      if (duel.length != 1) {
        return {};
      }
      return duel[0];
    },
    selectedRoundData: function() {
      let rounds = this.duelRounds;
      let selectedRound = this.selectedround;
      let round = rounds.filter(function(round) {
        return round["number"] == selectedRound;
      })
      if (round.length != 1) {
        return [];
      }
      return round[0];
    },
    formattedRoundScore: function() {
      if (this.selectedRoundData["score"]) {
        return this.selectedRoundData["score"]["opponent1"] + " : " + this.selectedRoundData["score"]["opponent2"];
      } else {
        return "---";
      }
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

function doScoreAdjustment(event) {
  let clickedId = event.target.id;
  let whom;
  let action;
  if (clickedId.includes("1")) {
    opponent = 1;
  } else {
    opponent = 2;
  }
  if (clickedId.includes("up")) {
    action = "UP";
  } else {
    action = "DOWN";
  }
  let duelId = vueApplication.selectedDuelData["id"];
  let roundId = vueApplication.selectedRoundData["id"];
  const POST_URL = "/run_duel/api/v1/duel/adjust";
  data = {
    duelid: duelId,
    action: action,
    opponent: opponent,
    roundid: roundId,
  }
  fetch(
    POST_URL,
    {
      method: "POST",
      body: JSON.stringify(data)
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if (json["success"]) {
      fetchDuelList();
    }
  })
}
