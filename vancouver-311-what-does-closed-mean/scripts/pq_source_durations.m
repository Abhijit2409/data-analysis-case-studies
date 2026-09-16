// Source_Durations: frequency table of recorded calendar days to closure for duration-eligible
// closed cases (prepared by 05_build_workbook.py), typed for nearest-rank percentile formulas.
let
    FilePath = Excel.CurrentWorkbook(){[Name = "DurationFile"]}[Content]{0}[Column1],
    Source = Csv.Document(File.Contents(FilePath), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"population", type text}, {"scope", type text},
        {"request_type", type text}, {"outcome_key", type text}, {"days_to_close", Int64.Type},
        {"records", Int64.Type}, {"cum_records", Int64.Type}})
in
    Typed
