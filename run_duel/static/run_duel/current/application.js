
var vueApplication = new Vue({
  el: '#vue',
  data: {
    "duel": {
      "duel_id": 0,
      "opponent1": {},
      "opponent2": {}
    },
    "rounds": []
  },
  computed: {
    currentRoundTimeRemaining: function() {
      let duel_time = 30000; //ms
      for (let i = 0; i < this.rounds.length; i++) {
        let round = this.rounds[i];
        if (
            (round["status"] === "RUNNING")
            || (round["status"] === "PAUSED")
        ) {
          let remaining = duel_time - round["time"];
          if (remaining < 0) {
            remaining = 0;
          }
          return (remaining / 1000.0).toFixed(0);
        }
      }
      // Default
      return "---";
    },
    currentRound: function() {
      let round = this.rounds.filter(function(round) {
        return (round["status"] === "RUNNING")
                || (round["status"] === "PAUSED");
      });
      if (round.length > 0) {
        return round[0];
      } else {
        return null;
      }
    },
    nextRound: function() {
      let round = this.rounds.filter(function(round) {
        return round["status"] == "READY";
      });
      if (round.length > 0) {
        return round[0];
      } else {
        return null;
      }
    },
    currentRoundOpponent1Score: function() {
      let round = this.currentRound;
      if (round) {
        return round["score"]["opponent1"];
      }
      return "---";
    },
    currentRoundOpponent2Score: function() {
      let round = this.currentRound;
      if (round) {
        return round["score"]["opponent2"];
      }
      return "---";
    },
    totalOpponent1Score: function() {
      let running_total = 0;
      for (let i = 0; i < this.rounds.length; i++) {
        let round = this.rounds[i];
        running_total += round["score"]["opponent1"];
      }
      return running_total;
    },
    totalOpponent2Score: function() {
      let running_total = 0;
      for (let i = 0; i < this.rounds.length; i++) {
        let round = this.rounds[i];
        running_total += round["score"]["opponent2"];
      }
      return running_total;
    },
    roundNumberDisplay: function() {
      let displayRound = this.currentOrNextRound;
      if (displayRound) {
        return displayRound["round_number"];
      }
      return "---";
    },
    roundStatusDisplay: function() {
      let displayRound = this.currentOrNextRound;
      if (displayRound) {
        return displayRound["status"];
      }
      return "ALL FINISHED";
    },
    currentOrNextRound: function() {
      let currentRound = this.currentRound;
      let nextRound = this.nextRound;
      if (currentRound) {
        return currentRound;
      }
      if (nextRound) {
        return nextRound;
      }
    }
  }
});

let timeNotifier = null;
let hpNotifier1 = null;
let hpNotifier2 = null;

function timeNotify() {
  let timeElement = document.getElementById("time");
  if (timeElement.classList.contains("flash")) {
    timeElement.classList.remove("flash");
  } else {
    timeElement.classList.add("flash");
  }

}

function startTimeNotifier() {
  timeNotifier = setInterval(timeNotify, 250);
}

function stopTimeNotifier() {
  clearInterval(timeNotifier);
  timeNotifier = null;
  let timeElement = document.getElementById("time");
  timeElement.classList.remove("flash");
}

function hp1Notify() {
  let hp1Element = document.getElementById("hp1");
  if (hp1Element.classList.contains("flash")) {
    hp1Element.classList.remove("flash");
  } else {
    hp1Element.classList.add("flash");
  }

}

function startHPNotifier1() {
  hpNotifier1 = setInterval(hp1Notify, 250);
}

function stopHPNotifier1() {
  clearInterval(hpNotifier1);
  hpNotifier1 = null;
  let hp1Element = document.getElementById("hp1");
  hp1Element.classList.remove("flash");
}

function hp2Notify() {
  let hp2Element = document.getElementById("hp2");
  if (hp2Element.classList.contains("flash")) {
    hp2Element.classList.remove("flash");
  } else {
    hp2Element.classList.add("flash");
  }

}

function startHPNotifier2() {
  hpNotifier2 = setInterval(hp2Notify, 250);
}

function stopHPNotifier2() {
  clearInterval(hpNotifier2);
  hpNotifier2 = null;
  let hp2Element = document.getElementById("hp2");
  hp2Element.classList.remove("flash");
}

// Web socket handling
let ws = null;
function manageWebSocketConnection() {
  ws = new WebSocket("{{ websocket_protocol }}://{{ base_url }}:{{ websocket_port }}/");
  ws.onmessage = function (event) {
    jsonData = JSON.parse(event.data);
    if (jsonData["success"]) {
      vueApplication.duel = jsonData["duel"];
      vueApplication.rounds = jsonData["rounds"];
    }
    // Notify if round over
    if (vueApplication.currentRoundTimeRemaining == "0") {
      if (!timeNotifier) {
        startTimeNotifier();
      }
    } else {
      stopTimeNotifier();
    }
    if (vueApplication.currentRoundOpponent1Score == 0) {
      if (!hpNotifier1) {
        startHPNotifier1();
      }
    } else {
      stopHPNotifier1();
    }
    if (vueApplication.currentRoundOpponent2Score == 0) {
      if (!hpNotifier2) {
        startHPNotifier2();
      }
    } else {
      stopHPNotifier2();
    }
  };
  ws.onclose = function () {
    ws = null;
    setTimeout(manageWebSocketConnection, 1000);
  }
}

manageWebSocketConnection();
