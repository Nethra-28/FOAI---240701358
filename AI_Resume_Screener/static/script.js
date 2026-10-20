const form =
    document.getElementById(
        "screenForm"
    );

const loading =
    document.getElementById(
        "loading"
    );

const resultsSection =
    document.getElementById(
        "resultsSection"
    );

const resultsBox =
    document.getElementById(
        "results"
    );

const errorBox =
    document.getElementById(
        "errorBox"
    );

const summary =
    document.getElementById(
        "summary"
    );


form.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        loading.classList.remove(
            "hidden"
        );


        resultsSection.classList.add(
            "hidden"
        );


        errorBox.classList.add(
            "hidden"
        );


        resultsBox.innerHTML = "";


        const formData =
            new FormData(form);


        try {

            const response =
                await fetch(
                    "/screen",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Screening failed."
                );

            }


            loading.classList.add(
                "hidden"
            );


            resultsSection.classList.remove(
                "hidden"
            );


            const results =
                data.results;


            const eligibleCount =
                results.filter(
                    r => r.eligible
                ).length;


            summary.innerHTML =

                `<strong>
                    ${eligibleCount}
                </strong>
                eligible candidate(s)
                out of
                <strong>
                    ${results.length}
                </strong>.
                Eligible candidates are ordered
                using Best-First Search.`;


            results.forEach(
                (candidate, index) => {

                    resultsBox.innerHTML +=
                        createCandidateCard(
                            candidate,
                            index
                        );

                }
            );


        }

        catch(error) {

            loading.classList.add(
                "hidden"
            );


            errorBox.classList.remove(
                "hidden"
            );


            errorBox.textContent =
                error.message;

        }

    }
);


function createCandidateCard(
    candidate,
    index
) {

    const statusClass =
        candidate.eligible
            ? "eligible"
            : "rejected";


    const statusText =
        candidate.eligible
            ? "ELIGIBLE"
            : "REJECTED";


    const constraintRows =
        candidate.constraint_trace
            .map(item => `

                <tr>

                    <td>
                        ${escapeHtml(
                            item.constraint
                        )}
                    </td>

                    <td>

                        <span
                            class="
                            status
                            ${
                                item.status ===
                                "PASS"
                                ? "pass"
                                : "fail"
                            }
                            "
                        >

                            ${item.status}

                        </span>

                    </td>

                    <td>

                        ${escapeHtml(
                            item.description
                        )}

                    </td>

                </tr>

            `)
            .join("");


    const backtrackingTrace =
        candidate.backtracking_trace

            .map(
                item =>
                    `<div>
                        ${escapeHtml(item)}
                    </div>`
            )

            .join("");


    const skills =
        candidate.skills.length

            ?

        candidate.skills
            .map(
                escapeHtml
            )
            .join(", ")

            :

        "No recognized skills";


    return `

        <div class="result-card">


            <div class="result-header">

                <div>

                    <h2>

                        ${index + 1}.
                        ${escapeHtml(
                            candidate.filename
                        )}

                    </h2>


                    <p class="${statusClass}">

                        <strong>
                            ${statusText}
                        </strong>

                    </p>

                </div>


                <div class="score">

                    ${candidate.heuristic_score}/100

                </div>

            </div>


            <table>

                <tr>

                    <th>
                        Extracted Field
                    </th>

                    <th>
                        Value
                    </th>

                </tr>


                <tr>

                    <td>
                        Degree
                    </td>

                    <td>

                        ${escapeHtml(
                            candidate.degree ||
                            "Not detected"
                        )}

                    </td>

                </tr>


                <tr>

                    <td>
                        CGPA
                    </td>

                    <td>
                        ${candidate.cgpa}
                    </td>

                </tr>


                <tr>

                    <td>
                        Experience
                    </td>

                    <td>
                        ${candidate.experience}
                        years
                    </td>

                </tr>


                <tr>

                    <td>
                        Skills
                    </td>

                    <td>
                        ${skills}
                    </td>

                </tr>


                <tr>

                    <td>
                        Email
                    </td>

                    <td>

                        ${escapeHtml(
                            candidate.email ||
                            "Not detected"
                        )}

                    </td>

                </tr>

            </table>


            <div class="algorithm-box">

                <h3>
                    1. CSP +
                    Constraint Propagation
                </h3>


                <p>

                    Hard constraints are
                    checked. A failed hard
                    constraint propagates
                    failure and removes the
                    candidate from the
                    eligible domain.

                </p>


                <table>

                    <tr>

                        <th>
                            Constraint
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Rule
                        </th>

                    </tr>

                    ${constraintRows}

                </table>

            </div>


            <div class="algorithm-box">

                <h3>
                    2. Backtracking Search
                </h3>


                <div class="trace">

                    ${backtrackingTrace}

                </div>

            </div>


            <div class="algorithm-box">

                <h3>
                    3. Heuristic Evaluation
                </h3>


                <ul>

                    <li>
                        Required skills:
                        50 points
                    </li>

                    <li>
                        Preferred skills:
                        20 points
                    </li>

                    <li>
                        Education:
                        15 points
                    </li>

                    <li>
                        CGPA:
                        10 points
                    </li>

                    <li>
                        Experience:
                        5 points
                    </li>

                </ul>


                <p>

                    <strong>

                        Heuristic Suitability
                        Score:

                        ${candidate.heuristic_score}/100

                    </strong>

                </p>

            </div>


            ${
                candidate.eligible

                ?

                `

                <div class="algorithm-box">

                    <h3>
                        4. Best-First Search
                    </h3>


                    <p>

                        This candidate is in
                        the eligible search space.
                        Candidates are expanded
                        in descending heuristic
                        score order.

                    </p>


                    <p>

                        <strong>
                            Best-First Search Order:
                        </strong>

                        ${candidate.search_order}

                    </p>

                </div>

                `

                :

                ""

            }


        </div>

    `;

}


function escapeHtml(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}