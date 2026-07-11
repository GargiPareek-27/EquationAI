# backend/evaluation/test_problems.py

TEST_PROBLEMS = [
    # --- Category: Basic arithmetic word problems ---
    {
        "id": "arith_01",
        "category": "arithmetic_word_problem",
        "problem": "Sara has 3 times as many apples as Tom. Together they have 20 apples. How many apples does Sara have?",
        "expected_answer": "15",
    },
    {
        "id": "arith_02",
        "category": "arithmetic_word_problem",
        "problem": "A store sells pens for $2 each and notebooks for $5 each. Ravi bought 4 pens and 3 notebooks. How much did he spend in total?",
        "expected_answer": "23",
    },

    # --- Category: Unit conversion / rate problems ---
    {
        "id": "rate_01",
        "category": "unit_conversion",
        "problem": "A train travels 60 km in 45 minutes. What is its speed in km/h?",
        "expected_answer": "80",
    },
    {
        "id": "rate_02",
        "category": "unit_conversion",
        "problem": "A car travels at 90 km/h for 2.5 hours. How far does it travel, in meters?",
        "expected_answer": "225000",
    },

    # --- Category: Systems of equations ---
    {
        "id": "algebra_01",
        "category": "systems_of_equations",
        "problem": "The sum of two numbers is 30 and their difference is 4. Find the larger number.",
        "expected_answer": "17",
    },

    # --- Category: Standard calculus (area, definite integrals) ---
    {
        "id": "calc_01",
        "category": "definite_integral",
        "problem": "Find the area under the curve y = x^2 from x = 0 to x = 3.",
        "expected_answer": "9",
    },
    {
        "id": "calc_02",
        "category": "area_between_curves",
        "problem": "Find the area between the curves y = x^2 and y = 4.",
        "expected_answer": "32/3",
    },

    # --- Category: Hard integration (substitution tricks) ---
    {
        "id": "calc_hard_01",
        "category": "hard_integration",
        "problem": "Evaluate the definite integral of x*sin(x) / (1 + cos^2(x)) from 0 to pi.",
        "expected_answer": "pi**2/4",
    },
    {
        "id": "calc_hard_02",
        "category": "hard_integration",
        "problem": "Evaluate the definite integral of ln(1 + tan(x)) from 0 to pi/4.",
        "expected_answer": "pi*log(2)/8",
    },

    # --- Category: Deliberately ambiguous / unsolvable (tests is_solvable handling) ---
    {
        "id": "ambiguous_01",
        "category": "ambiguous_input",
        "problem": "Find x.",
        "expected_answer": None,  # should be flagged is_solvable: false
    },
    {
        "id": "ambiguous_02",
        "category": "ambiguous_input",
        "problem": "John is twice as old as his friend. How old is John?",
        "expected_answer": None,  # underspecified — no absolute age given
    },

    # --- Category: Nonsensical / adversarial input (tests robustness) ---
    {
        "id": "nonsense_01",
        "category": "nonsensical_input",
        "problem": "What color is the number seven?",
        "expected_answer": None,  # should gracefully decline, not crash
    },
    # --- Category: Differential equations ---
    {
        "id": "de_01",
        "category": "differential_equations",
        "problem": "Solve the differential equation dy/dx = 2xy with the initial condition y(0) = 1.",
        "expected_answer": "exp(x**2)",
    },
    {
        "id": "de_02",
        "category": "differential_equations",
        "problem": "Find the general solution to the differential equation y'' - 5y' + 6y = 0.",
        "expected_answer": None,  # multiple equivalent forms possible (C1*exp(2x)+C2*exp(3x)) — check manually, not auto-scored
    },

    # --- Category: Probability / combinatorics ---
    {
        "id": "prob_01",
        "category": "probability",
        "problem": "A bag contains 5 red balls and 3 blue balls. If 2 balls are drawn at random without replacement, what is the probability that both are red?",
        "expected_answer": "5/14",
    },
    {
        "id": "prob_02",
        "category": "combinatorics",
        "problem": "In how many ways can 4 distinct books be arranged on a shelf if 2 specific books must always be next to each other?",
        "expected_answer": "12",
    },

    # --- Category: Geometry / coordinate geometry ---
    {
        "id": "geo_01",
        "category": "coordinate_geometry",
        "problem": "Find the distance between the points (3, 4) and (-1, 1).",
        "expected_answer": "5",
    },
    {
        "id": "geo_02",
        "category": "coordinate_geometry",
        "problem": "Find the equation of the line passing through (2, 3) and (4, 7), in the form y = mx + c.",
        "expected_answer": None,  # y = 2x - 1 — check manually, multiple valid representations
    },

    # --- Category: Series / sequences ---
    {
        "id": "series_01",
        "category": "series",
        "problem": "Find the sum of the infinite geometric series 1 + 1/3 + 1/9 + 1/27 + ...",
        "expected_answer": "3/2",
    },

    # --- Category: Matrices / linear algebra ---
    {
        "id": "matrix_01",
        "category": "linear_algebra",
        "problem": "Find the determinant of the matrix [[2, 3], [4, 1]].",
        "expected_answer": "-10",
    },

    # --- Category: Genuinely hard integration (another substitution-trick problem, less famous than the King's Property ones) ---
    {
        "id": "calc_hard_03",
        "category": "hard_integration",
        "problem": "Evaluate the integral of 1/(1 + sqrt(x)) dx.",
        "expected_answer": None,  # 2*sqrt(x) - 2*log(1+sqrt(x)) + C — indefinite, has a constant of integration, check manually
    },

    # --- Category: A trickier ambiguous case (tests whether the LLM over-assumes) ---
    {
        "id": "ambiguous_03",
        "category": "ambiguous_input",
        "problem": "A rectangle has a perimeter of 20. What is its area?",
        "expected_answer": None,  # genuinely underdetermined — infinitely many rectangles have perimeter 20 with different areas
    },
]