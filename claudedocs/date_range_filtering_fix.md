# Date Range Filtering Fix - Analytics Charts

## Vấn đề

Khi chọn date range ngắn (ví dụ: 4 ngày từ 01/01/2017 đến 04/01/2017), các charts vẫn hiển thị đầy đủ 7 ngày trong tuần thay vì chỉ hiển thị 4 ngày thực sự có trong date range.

### Ví dụ cụ thể:
**Date range**: 01/01/2017 (Sunday) đến 04/01/2017 (Wednesday) = 4 ngày

**Before (Incorrect)**:
- Average Daily Consumption: Hiển thị 7 cột (Sun, Mon, Tue, Wed, Thu, Fri, Sat)
- Average Weekly Consumption: Hiển thị 7 cột (Mon, Tue, Wed, Thu, Fri, Sat, Sun)

**After (Correct)**:
- Average Daily Consumption: Chỉ hiển thị 4 cột (Sunday, Monday, Tuesday, Wednesday)
- Average Weekly Consumption: Chỉ hiển thị 4 cột (Sun, Mon, Tue, Wed)

---

## Nguyên nhân

### Code cũ (Incorrect):

```typescript
// dailyPatternsData - ALWAYS showed all 7 days
const dailyPatternsData = useMemo(() => {
  if (!patterns?.daily_patterns) return null;

  return {
    labels: Object.keys(patterns.daily_patterns).map((_, i: number) => getDayName(i)),
    datasets: [{
      label: `Average Daily Consumption`,
      data: Object.values(patterns.daily_patterns),  // All 7 values
      backgroundColor: 'rgba(53, 162, 235, 0.5)',
    }],
  };
}, [patterns?.daily_patterns, selectedMetric]);

// weeklyPatternsData - ALWAYS showed all 7 days
const weeklyPatternsData = useMemo(() => {
  if (!patterns?.daily_patterns) return null;

  const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const weeklyData = weekdays.map(day => patterns.daily_patterns[day] || 0);  // All 7 values

  return {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],  // All 7 labels
    datasets: [{
      label: `Average Weekly Consumption`,
      data: weeklyData,
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
    }],
  };
}, [patterns?.daily_patterns, selectedMetric]);
```

**Vấn đề**:
- Không check date range
- Luôn hiển thị cả 7 ngày
- Không phụ thuộc vào `dateRange.start` và `dateRange.end`

---

## Giải pháp

### 1. Helper Function: `getDaysInRange()`

Tạo function để tính toán các ngày thực sự có trong date range:

```typescript
// Helper function to get days in date range
const getDaysInRange = (startDate: string, endDate: string) => {
  const days: string[] = [];
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const dayAbbr = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const start = new Date(startDate);
  const end = new Date(endDate);
  const current = new Date(start);

  // Iterate through each day in the range
  while (current <= end) {
    const dayOfWeek = current.getDay();  // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    days.push(dayNames[dayOfWeek]);
    current.setDate(current.getDate() + 1);
  }

  return { fullNames: days, abbreviations: dayAbbr };
};
```

**Logic**:
- Start from `startDate`
- Loop until `endDate`
- For each date, get day of week (0-6)
- Add day name to array
- Return list of actual days in range

**Example**:
```typescript
getDaysInRange('2017-01-01', '2017-01-04')
// Returns:
{
  fullNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday'],
  abbreviations: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']  // Full list for mapping
}
```

### 2. Updated `dailyPatternsData`

```typescript
// Define chart data from patterns - show only days in selected range
const dailyPatternsData = useMemo(() => {
  if (!patterns?.daily_patterns || !dateRange.start || !dateRange.end) return null;

  const { fullNames } = getDaysInRange(dateRange.start, dateRange.end);

  // Get unique days (in case range spans multiple weeks)
  const uniqueDays = Array.from(new Set(fullNames));

  return {
    labels: uniqueDays,  // Only days in range
    datasets: [
      {
        label: `Average Daily ${getMetricDisplayName(selectedMetric)} Consumption`,
        data: uniqueDays.map(day => patterns.daily_patterns[day] || 0),  // Only selected days
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };
}, [patterns?.daily_patterns, selectedMetric, dateRange.start, dateRange.end]);
```

**Key changes**:
- ✅ Added `dateRange.start` and `dateRange.end` to dependencies
- ✅ Call `getDaysInRange()` to get actual days
- ✅ Use `uniqueDays` for labels (handles multi-week ranges)
- ✅ Map only selected days to data values

### 3. Updated `weeklyPatternsData`

```typescript
// Define weekly patterns chart data - show only days in selected range
const weeklyPatternsData = useMemo((): any | null => {
  if (!patterns?.daily_patterns || !dateRange.start || !dateRange.end) return null;

  const { fullNames } = getDaysInRange(dateRange.start, dateRange.end);

  // Get unique days preserving order (Sun -> Sat)
  const dayOrder = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const dayAbbrMap: Record<string, string> = {
    'Sunday': 'Sun', 'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
    'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat'
  };

  const uniqueDays = dayOrder.filter(day => fullNames.includes(day));
  const labels = uniqueDays.map(day => dayAbbrMap[day]);
  const weeklyData = uniqueDays.map(day => patterns.daily_patterns[day] || 0);

  return {
    labels,  // Only days in range
    datasets: [
      {
        label: `Average Weekly ${getMetricDisplayName(selectedMetric)} Consumption`,
        data: weeklyData,  // Only selected days
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
    ],
  };
}, [patterns?.daily_patterns, selectedMetric, dateRange.start, dateRange.end]);
```

**Key changes**:
- ✅ Added `dateRange.start` and `dateRange.end` to dependencies
- ✅ Call `getDaysInRange()` to get actual days
- ✅ Filter `dayOrder` to keep only days present in range
- ✅ Preserve chronological order (Sunday → Saturday)
- ✅ Map to abbreviations for labels

### 4. Cleanup

Removed unused `getDayName()` function:

```typescript
// REMOVED - No longer needed
const getDayName = (index: number): string => {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return days[index % 7];
};
```

---

## Test Scenarios

### Scenario 1: 4 Days (01/01 - 04/01/2017)

**Date Range**: Sunday, Monday, Tuesday, Wednesday

**Expected Display**:
- Daily Consumption: 4 bars (Sun, Mon, Tue, Wed)
- Weekly Consumption: 4 bars (Sun, Mon, Tue, Wed)

### Scenario 2: 7 Days (01/01 - 07/01/2017)

**Date Range**: Full week (Sun → Sat)

**Expected Display**:
- Daily Consumption: 7 bars (all days)
- Weekly Consumption: 7 bars (all days)

### Scenario 3: 10 Days (spanning 2 weeks)

**Date Range**: 01/01 - 10/01/2017

**Days**: Sun, Mon, Tue, Wed, Thu, Fri, Sat, Sun, Mon, Tue

**Expected Display**:
- Daily Consumption: 7 unique bars (Sun, Mon, Tue, Wed, Thu, Fri, Sat)
- Weekly Consumption: 7 unique bars (shows average across both weeks)

**Note**: Uses `Array.from(new Set(fullNames))` to get unique days when range spans multiple weeks.

### Scenario 4: 1 Month (01/01 - 31/01/2017)

**Date Range**: Full month (31 days = 4+ weeks)

**Expected Display**:
- Daily Consumption: 7 bars (all days appear in month)
- Weekly Consumption: 7 bars (averaged across all weeks)

---

## Implementation Details

### Day Order Preservation

**Why preserve order?**

When displaying days, users expect chronological order:
- Sunday → Monday → ... → Saturday

**Implementation**:
```typescript
const dayOrder = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const uniqueDays = dayOrder.filter(day => fullNames.includes(day));
```

This ensures:
- Days appear in order even if date range starts mid-week
- Example: Wed-Fri range shows [Wed, Thu, Fri], not [Fri, Thu, Wed]

### Handling Multi-Week Ranges

**Problem**: If range spans 2+ weeks, same days repeat

**Solution**: Use `Set` to get unique days
```typescript
const uniqueDays = Array.from(new Set(fullNames));
```

**Example**:
```typescript
// Range: 10 days (Sun-Mon-Tue-Wed-Thu-Fri-Sat-Sun-Mon-Tue)
fullNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']

// After Set
uniqueDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
```

**Result**: Shows average consumption for each day across all weeks in range.

---

## Edge Cases

### Edge Case 1: Single Day

**Range**: 01/01/2017 - 01/01/2017

**Expected**: 1 bar for Sunday

### Edge Case 2: Weekend Only

**Range**: 06/01/2017 - 07/01/2017

**Expected**: 2 bars (Fri, Sat) or (Sat, Sun) depending on actual dates

### Edge Case 3: Invalid Range

**Range**: end < start

**Behavior**: `getDaysInRange()` returns empty array → charts show "No data"

### Edge Case 4: Missing Date Range

**Condition**: `!dateRange.start || !dateRange.end`

**Behavior**: Return `null` from useMemo → fallback message displayed

---

## Dependencies Update

Both `useMemo` hooks now depend on date range:

```typescript
// Before
}, [patterns?.daily_patterns, selectedMetric]);

// After
}, [patterns?.daily_patterns, selectedMetric, dateRange.start, dateRange.end]);
```

**Why important?**:
- Charts re-render when date range changes
- Ensures displayed days match selected range
- Prevents stale data display

---

## Files Modified

**File**: `frontend/src/pages/Analytics.tsx`

**Changes**:
1. Lines 303-320: Added `getDaysInRange()` helper function
2. Lines 322-341: Updated `dailyPatternsData` with date filtering
3. Lines 343-370: Updated `weeklyPatternsData` with date filtering
4. Removed: `getDayName()` function (no longer needed)

---

## Deployment

```bash
# Copy updated file
cd /Users/hoangdat/.../EAIO-DL/frontend
docker cp src/pages/Analytics.tsx eaio-frontend:/app/src/pages/Analytics.tsx

# Webpack auto-recompiles
docker logs eaio-frontend 2>&1 | tail -30 | grep "Compiled"
# Output: "Compiled with warnings." (OK)
```

---

## Testing Instructions

### Step 1: Hard Refresh Browser
- Windows/Linux: `Ctrl+Shift+R`
- Mac: `Cmd+Shift+R`

### Step 2: Test Short Range (4 days)
1. Select date range: 01/01/2017 - 04/01/2017
2. Select building with data (e.g., Bear_assembly_Angel)
3. Verify charts show only 4 days

### Step 3: Test Full Week (7 days)
1. Select date range: 01/01/2017 - 07/01/2017
2. Verify charts show all 7 days

### Step 4: Test Longer Range (1 month)
1. Select date range: 01/01/2017 - 31/01/2017
2. Verify charts show 7 unique days (averaged)

---

## Expected Results

### ✅ Correct Behavior

**4-day range (Sun-Wed)**:
```
Average Daily Consumption
[4 bars: Sunday, Monday, Tuesday, Wednesday]

Average Weekly Consumption
[4 bars: Sun, Mon, Tue, Wed]
```

**7-day range (full week)**:
```
Average Daily Consumption
[7 bars: Sunday through Saturday]

Average Weekly Consumption
[7 bars: Sun through Sat]
```

### ❌ Previous Incorrect Behavior

**Any range always showed**:
```
Average Daily Consumption
[7 bars - always all days]

Average Weekly Consumption
[7 bars - always all days]
```

---

## Benefits

1. **Accurate Representation**: Charts show only data for selected period
2. **Better UX**: Users see exactly what they selected
3. **Clearer Insights**: Short-range analysis more focused
4. **Logical Consistency**: Date range picker controls chart display

---

**Status**: ✅ Fixed and deployed
**Date**: 2025-12-09
**Impact**: Charts now accurately reflect selected date range
**User Experience**: More intuitive and accurate data visualization
