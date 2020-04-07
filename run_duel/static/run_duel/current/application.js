
var vueApplication = new Vue({
  el: '#vue',
  data: {
    "duel": {
      "duel_id": 0,
      "opponent1": {},
      "opponent2": {},
      "rounds": []
    }
  },
  computed: {
    currentRoundTimeRemaining: function() {
      let duel_time = 30000; //ms
      let round = this.currentRound;
      if (!round) {
        // No round is active
        return "---";
      } else {
        let remaining = duel_time - round["time"];
        if (remaining < 0) {
          remaining = 0;
        }
        return (remaining / 1000.0).toFixed(0);
      }
    },
    currentRound: function() {
      let rounds = this.duel.rounds.filter(
        round => (
          round["status"] === "RUNNING")
          || (round["status"] === "PAUSED"
        )
      );
      if (rounds.length > 0) {
        return rounds[0];
      } else {
        return null;
      }
    },
    nextRound: function() {
      let rounds = this.duel.rounds.filter(
        round => round["status"] == "READY"
      );
      if (rounds.length > 0) {
        return rounds[0];
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
      let scores = this.rounds.map(
        round => round["score"]["opponent1"]
      );
      if (scores.length == 0) {
        return "---";
      }
      return scores.reduce(
        accumulator, value => (accumulator + value)
      );
    },
    totalOpponent2Score: function() {
      let scores = this.rounds.map(
        round => round["score"]["opponent2"]
      );
      if (scores.length == 0) {
        return "---";
      }
      return scores.reduce(
        accumulator, value => (accumulator + value)
      );
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

/*
 * When time is up or when
 * an opponent has completely
 * depleted their HP
 * then a function set via
 * setInterval flashes the
 * background red/black as
 * and indicator
 * References to these
 * 'interval objects' are
 * kept in these variables
 * so the flashing can be
 * stopped when
 * the round is stopped
 */
let timeNotifier = null;
let hpNotifier1 = null;
let hpNotifier2 = null;

/*
 * Each of three possible
 * items that can have a
 * flashing background to
 * indicate that they are
 * depleted (time, hp 1/2)
 * has a trio of methods
 * to manage the flashing effect
 * xNotify actually does the
 * work of toggling the
 * background colour
 * startXNotifierY initiates the
 * flashing by setting the interval
 * Note that it stores a
 * reference to the 'interval'
 * in the applicable variable, above
 * stopXNotifierY stops the flashing
 * and ensures that the background
 * has been reverted to normal
 */

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

// Manage flashing on/off
function manageNotifiers() {
  /*
   * If the round time is up
   * and the timer is not yet flashing
   * then start it flashing
   */
  if (vueApplication.currentRoundTimeRemaining == "0" && !timeNotifier) {
    startTimeNotifier();
  }
  /*
   * If the round time is not up
   * but the time is flashing
   * stop it from flashing
   */
  if (vueApplication.currentRoundTimeRemaining != "0" && timeNotifier) {
    stopTimeNotifier();
  }
  /*
   * If the opponent 1's hp is depleted
   * and the hp display is not yet flashing
   * then start it flashing
   */
  if (vueApplication.currentRoundOpponent1Score == 0 && !hpNotifier1) {
    startHPNotifier1();
  }
  /*
   * If opponent 1's hp has not yet been depleted
   * but the hp display is still flashing
   * then turn off the flashing
   */
  if (vueApplication.currentRoundOpponent1Score != 0 && hpNotifier1) {
    stopHPNotifier1();
  }
  // As previous two ifs, for opponent 2
  if (vueApplication.currentRoundOpponent2Score == 0 && !hpNotifier2) {
    startHPNotifier2();
  }
  if (vueApplication.currentRoundOpponent2Score != 0 && hpNotifier2) {
    stopHPNotifier2();
  }
}

// Web socket handling
let ws = null;
function manageWebSocketConnection() {
  ws = new WebSocket(
    WEBSOCKET_PROTOCOL
    + "://"
    + WEBSOCKET_URL
    + ":"
    + WEBSOCKET_PORT
    + "/"
  );
  ws.onmessage = function (event) {
    let json = JSON.parse(event.data);
    if (json["success"]) {
      vueApplication.duel = json;
    }
    manageNotifiers();
  };
  // Attempt to reopen on close
  ws.onclose = function () {
    ws = null;
    setTimeout(manageWebSocketConnection, 1000);
  }
}

manageWebSocketConnection();
