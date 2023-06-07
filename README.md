**The biggest feature is I added Pydantic models for nearly everything for both REST endpoints as well as formally defining the streaming messages.**
Look at the samples folder where nearly every endpoint and streaming API service is tested.
Repo link: [https://github.com/primalmachina/pm-td-ameritrade-api](https://github.com/primalmachina/pm-td-ameritrade-api)

**Other TDA repos:**
The original version I edited, which was the main inspiration for the code structure: [https://github.com/areed1192/td-ameritrade-api](https://github.com/areed1192/td-ameritrade-api)
Another version I used at least for base orders classes: [https://github.com/alexgolec/tda-api](https://github.com/alexgolec/tda-api)

1) **Authentication and Configuration:** Now handled automatically through a config file specified with an environment variable, TD_API_CONFIG_PATH, this config file automates the login/auth process using Selenium all done through a new Config.py module.
Here's an example of what it looks like:

found in samples/z-config-example.ini

[app_info]
app_name = meep
client_id = meepmeep
redirect_uri = https://127.0.0.1:XXXX
[credentials]
username = meepmeepmeep
account_password = meepmeepmeepmeepmeep
secretquestion0 = General
secretanswer0 = Kenobi
secretquestion1 = Secret to life
secretanswer1 = 42
secretquestion2 = Favorite color
secretanswer2 = Blue! No..wait-AHHHHHHHHH!
secretquestion3 = Should you revenge trade
secretanswer3 = No
[accounts]
default = 123456789
ROTH_IRA = 123456789
TRADITIONAL_IRA = 123456789
CASH = 123456789
MARGIN = 123456789
[logging]
log_root_path = C://Users//meep//OneDrive//Desktop//meep//td-ameritrade-api//logs
use_bulk_app_name_logging = True
[symbols]
full_equities_path = .../tda-symbols.csv
tda_futures_path = .../tda-futures.csv
actively_traded_equities_path = .../tda-actively-traded-equities.csv
[data_paths]
equity_data_base_path = .../tda-data/equity
futures_data_base_path = .../tda-data/future

So now in terms of the login flow/process, if the environment variable is specified, you can just do this:

```td_client = TdAmeritradeClient()```

instead of...

```
# Initialize the Parser.
config = ConfigParser()
# Read the file.
config.read('config/config.ini')
# Get the specified credentials.
client_id = config.get('main', 'client_id')
redirect_uri = config.get('main', 'redirect_uri')
# Intialize our `Credentials` object.
td_credentials = TdCredentials(
client_id=client_id,
redirect_uri=redirect_uri,
credential_file='config/td_credentials.json'
)
# Initalize the `TdAmeritradeClient`
td_client = TdAmeritradeClient(
credentials=td_credentials
)
```

2) **Added Logging:** Colored logging is now done to the console, and, if specified, to a logging directory specified in the config.ini file. In the config file, use_bulk_app_name_logging, dictates whether, in addition to module-level logging, all logging is written to the log file specified by app_name.
Also, for logging, I added variables to the client for whether you want to log sent/received messages. I have log sent True and log received as fault for both REST api and streaming api by default.
`td_client = TdAmeritradeClient(log_sent_messages=True, log_received_messages=True)`
Debug logging - Program will look for the environment variable, TD_API_DEBUG, set to True or False.

3) **Pydantic Models for dataclasses and validation - REST / Orders:** In td/models I added a variety of models for various things in the api. For the REST endpoints, I have a decorator called QueryInitializer, that specifies the model for the function in a specific service (e.g. Price History service, price_history.py, has a get_price_history function, decorated with "@QueryInitializer(PriceHistoryQuery)" that allows three different calling methods:

```python
            1. Population by field names specified in `PriceHistoryQuery`
 >>> price_history_service = td_client.price_history()
 >>> price_history = price_history_service.get_price_history(
                    symbol="MSFT",
                    frequency_type=FrequencyType.DAILY,
                    frequency=1,
                    period_type=PeriodType.MONTH,
                    period=1,
                    extended_hours_needed=False,
                )
            2. Pass a dictionary with field names specified in `PriceHistoryQuery`
 >>> price_history = price_history_service.get_price_history({
                    "symbol": "MSFT",
                    "frequency_type": FrequencyType.DAILY,
                    "frequency": 1,
                    "period_type": PeriodType.MONTH,
                    "period": 1,
                    "extended_hours_needed": False,
                })

            3. Pass an `PriceHistoryQuery` object directly
 >>> price_history_query = PriceHistoryQuery(**{
                    "symbol": "MSFT",
                    "frequency_type": FrequencyType.DAILY,
                    "frequency": 1,
                    "period_type": PeriodType.MONTH,
                    "period": 1,
                    "extended_hours_needed": False,
                })
 >>> price_history = price_history_service.get_price_history(price_history_query)

Orders has a recursive model defined in orders.py. I agree with Alex Golec's interpretation that an Order builder was best but I reworked the builder class in orders/builder.py to be more concise and use pydantic.

4) **Pydantic Models for dataclasses and validation - Streaming:** The streaming messages, with the exception of order activity, all have formal Pydantic models defined. Take a look at samples/example_handlers.py for how to use them. In general, there's a BaseDataMessageHandler that acts as a dynamic initializer. There are also, BaseChartHistoryHandler, and BaseActivesHandler..

5) **Synchronous or Asynchronous asyncio usage of streaming API:** See samples/stream_client/use_synchronously.py vs something like samples/stream_client/quotes/use_level_one.py

6) **Ability to use camelCase or snake_case for Pydantic models:** All models have an alias generator for camelCase so they can use either. This is also used in sending a payload. Although the data classes have snake_case, sending a request with by_alias=True, allows conversion into what the API endpoints expect.

```res = self.session.make_request(
 method="get",
 endpoint=f"marketdata/{movers_query.index}/movers",
 params=movers_query.dict(by_alias=True),
 )
 ```

7) **Various other touch-ups and reworking of the code:** Like reviewing documentation, touching up and making sure enums were correct, consolidating helper functions, etc.

**Future:** Who knows how much the API will change with the Schwab merger/acquisition. I plan to update the API further and would love help if people are willing.

0) Possibly add working code for saved orders and watchlists. I did not spend the time since I currently don't use them and they're being removed by Schwab.
1) All testing is currently done by manually calling the sample files. This isn't nearly robust enough and a testing strategy needed to be developed.
2) Handling the Order Activity service and parsing the XML from there and converting that into Pydantic models is a task I wasn't ready to tackle yet. In addition, for now, I don't have the code for watchlists or saved_orders since Schwab plans to remove them. If someone wants to add that code back in I'd be happy to merge a PR
3) Added more types of orders and examples (e.g. stop loss orders)
4) Sync/async of REST endpoints: I plan to do this same type of interface of having an event loop running in the background for the main REST endpoints and also allow those to be async/sync soon. So using aiohttp in the future, maybe do asynchronous logging at the same time as well as look at where else async can be used.
5) Better documentation of validation for rest endpoints. Although using Pydantic and QueryInitializer is neat, convenient, and concise, when hovering over a function definition, it just says it takes the model but doesn't specify exactly what it expects. This could use some work. Not sure how to go about that at this point.
6) Long-term goal is something akin to how to make the API "pluggable" into an event-based trading architecture.

**Discord:**

I made a discord if anyone is interested. [Join Discord](https://discord.gg/a3eHnNhF)
