# Data Releases
- Sprint 1: Initial datasets released + students to find their own datasets.
- Sprint 2: More datasets released + business rules.
- Sprint 3: Final batch of datasets released.

The data will either be provided by an annoucement (downloadable via URL) or uploaded directly to the `raw` directory.

## Folder Specification
1. Domain dataset
   - save [domain website]('https://www.domain.com.au/') rent-house dataset
        ```
            |-- data
                    |-- raw
                            |-- domain-website-data
        ```

2. External dataset
   - save pre-external dataset
        ```
            |-- data
                    |-- external-raw-data
        ```
   - save external dataset
        ```
            |-- data
                    |-- raw
                            |-- external-data
        ```

3. preprocessing
   - save openrouteserveice dataset
        ```
            |- data
                    |- raw
                            |- ors-data
        ```
   - save preprocessed domain website dataset
        ```
            |- data
                    |- curated
                            |- domain-website-data
        ```
   - save external feature dataset
        ```
            |- data
                    |- curated
                            |- external-data
        ```
   - save model dataset
        ```
            |- data
                    |- curated
                            |- model-data
        ```