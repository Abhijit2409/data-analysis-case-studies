// Source_Data: cleaned 2025 cohort -> analyst-defined outcome groups -> grouped record counts.
// The outcome mapping comes from the workbook table tblClosureMapping, so editing that
// table and refreshing re-groups every closure reason. Unmapped values are labelled, not dropped.
let
    FilePath = Excel.CurrentWorkbook(){[Name = "DataFile"]}[Content]{0}[Column1],
    Source = Csv.Document(File.Contents(FilePath), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Kept = Table.SelectColumns(Promoted, {"open_month", "department", "service_request_type", "channel", "status",
        "closure_reason", "admin_sounding", "focus_family", "local_area", "duration_exclusion_reason", "duplicate_looking"}),
    Typed = Table.TransformColumnTypes(Kept, {{"open_month", Int64.Type}, {"department", type text},
        {"service_request_type", type text}, {"channel", type text}, {"status", type text}, {"closure_reason", type text},
        {"admin_sounding", type text}, {"focus_family", type text}, {"local_area", type text},
        {"duration_exclusion_reason", type text}, {"duplicate_looking", type text}}),
    Mapping = Excel.CurrentWorkbook(){[Name = "tblClosureMapping"]}[Content],
    MapCols = Table.SelectColumns(Mapping, {"Closure reason (original)", "Outcome group (analyst-defined)"}),
    Merged = Table.NestedJoin(Typed, {"closure_reason"}, MapCols, {"Closure reason (original)"}, "Map", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "Map", {"Outcome group (analyst-defined)"}, {"outcome_group"}),
    Flagged = Table.ReplaceValue(Expanded, null, "6. Other - requires review (UNMAPPED)", Replacer.ReplaceValue, {"outcome_group"}),
    Grouped = Table.Group(Flagged, {"open_month", "department", "service_request_type", "channel", "status",
        "closure_reason", "outcome_group", "admin_sounding", "focus_family", "local_area", "duration_exclusion_reason",
        "duplicate_looking"}, {{"records", each Table.RowCount(_), Int64.Type}}),
    Sorted = Table.Sort(Grouped, {{"open_month", Order.Ascending}, {"department", Order.Ascending},
        {"service_request_type", Order.Ascending}, {"closure_reason", Order.Ascending}})
in
    Sorted
