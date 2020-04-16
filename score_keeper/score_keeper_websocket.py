
import asyncio
import json
import requests
import time
import websockets

# Track who is connected to the websocket server
CONNECTIONS = []

# Store last two statuses
PREVIOUS_STATUS = {}
THIS_STATUS = {}


# Maximum number of requests
# before sending even if
# status hasn't changed
MAXIMUM_REQUESTS = 5


# Register new connection
def register(websocket):
    CONNECTIONS.append(websocket)


# Unregister dropped connection
async def unregister():
    # May as well get rid
    # of all closed
    await drop_closed()


# Register new connections, forget dropped ones
async def handler(websocket, path):
    register(websocket)
    print("OPEN: ", len(CONNECTIONS))
    try:
        first_pass = True
        while True:
            # Pass location of this websocket in connections array
            if not first_pass:
                # On all passes except first
                # wait up to 5 requests for
                # something to change before
                # sending status update
                message = await status_update(
                    CONNECTIONS.index(websocket),
                    MAXIMUM_REQUESTS
                )
            else:
                # On first pass only
                # make one request
                # before sending an update
                message = await status_update(
                    CONNECTIONS.index(websocket),
                    0
                )
            # Always drop closed connections
            # before sending
            await drop_closed()
            # Exit if this websocket connection is lost
            if websocket not in CONNECTIONS:
                break
            if CONNECTIONS:
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosedOK:
                    pass
            first_pass = False
    finally:
        await unregister()
        print("CLOSE: ", len(CONNECTIONS))


async def status_update(
        websocket_number,
        maximum_requests
):
    global PREVIOUS_STATUS
    global THIS_STATUS
    # Until there is a status change
    loop_counter = 0
    while True:
        loop_counter += 1
        # TODO choose best value
        # Don't make too many requests!
        await asyncio.sleep(0.2)
        # Only one 'thread' should fetch
        # updates and store it in tracking variable
        # Take first websocket connection in array
        if websocket_number == 0:
            # Get latest data
            try:
                response = requests.get("http://localhost:8000/run_duel/api/v1/event_stream")
            except requests.exceptions.ConnectionError:
                # Return json to indicate failure
                # if not possible
                return json.dumps(
                    {
                        "success": False
                    }
                )
            # Make copy of current status
            PREVIOUS_STATUS = THIS_STATUS
            # Get latest status
            THIS_STATUS = json.loads(
                response.content.decode("utf-8")
            )
            THIS_STATUS["success"] = True
        if (
                THIS_STATUS != PREVIOUS_STATUS
                or loop_counter > maximum_requests
        ):
            return json.dumps(THIS_STATUS)


# Ditch closed connections regularly
# (try finally seems not to work)
async def drop_closed():
    for i in range(len(CONNECTIONS)):
        if i < len(CONNECTIONS):
            try:
                connection = CONNECTIONS[i]
                if not connection.open:
                    CONNECTIONS.pop(i)
                    print("DROPPED 1, REMANING: ", len(CONNECTIONS))
            except IndexError:
                pass


start_server = websockets.serve(
    handler,
    "localhost",
    8001
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
