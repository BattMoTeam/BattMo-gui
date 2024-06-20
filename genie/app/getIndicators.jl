module getIndicators

    import BattMo, Jutul
    export getIndicators

    function getIndicatorsBattMo(input_file)
        println("input = ",input_file)
        init = BattMo.JSONFile(input_file)
        println("init = ",init)

        specs = BattMo.computeCellSpecifications(init)

        return specs
    end

end