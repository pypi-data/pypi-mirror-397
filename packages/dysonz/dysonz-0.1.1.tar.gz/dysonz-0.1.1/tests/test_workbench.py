from dysonz.workbench import Workbench

def test_workbench():

    recipes = [
        {
            "inputs": {"iron": 1, "coal": 3, "aluminum": 2},
            "outputs": {"sword": 1}
        }
    ]

    bench = Workbench(
        total_capacity=100,
        resource_limits={"iron": 30, "coal": 40, "aluminum": 30},
        recipes=recipes,
        cleanup_timeout=60
    )

    bench.add_resource("iron", 15)
    bench.add_resource("coal", 23)
    bench.add_resource("aluminum", 10)

    bench.produce_until_exhausted()

    print(bench.status())

    sent_products = bench.dispatch()

    for lot in sent_products:
        print(lot.product, lot.amount, lot.cost)
