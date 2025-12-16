# Average Weekly Consumption Chart Fix

## Vấn đề

"Average Weekly Consumption" chart chỉ hiển thị 1 cột duy nhất (Wednesday) thay vì 7 cột cho 7 ngày trong tuần.

---

## Nguyên nhân

### Code ban đầu (INCORRECT):
```typescript
// Line 320-333 in Analytics.tsx
const weeklyPatternsData = useMemo((): any | null => {
  if (!patterns?.weekly_patterns) return null;

  return {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: `Average Weekly Consumption`,
      data: Object.values(patterns.weekly_patterns) as number[],  // ❌ WRONG
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
    }],
  };
}, [patterns?.weekly_patterns, selectedMetric]);
```

### Tại sao sai?

`patterns.weekly_patterns` chỉ có structure:
```json
{
  "highest_day": "Monday",
  "lowest_day": "Saturday",
  "weekday_weekend_ratio": 1.07
}
```

Khi gọi `Object.values(patterns.weekly_patterns)`:
- Trả về: `["Monday", "Saturday", 1.07]`
- Chart.js chỉ render giá trị number: `1.07`
- Kết quả: Chỉ 1 cột với giá trị 1.07 (quá nhỏ để thấy rõ)

### Dữ liệu đúng nằm ở đâu?

`patterns.daily_patterns` mới có 7 giá trị cho 7 ngày:
```json
{
  "Monday": 540.0,
  "Tuesday": 540.0,
  "Wednesday": 540.0,
  "Thursday": 540.0,
  "Friday": 540.0,
  "Saturday": 504.7,
  "Sunday": 504.7
}
```

---

## Giải pháp

### Code mới (CORRECT):
```typescript
// Line 320-337 in Analytics.tsx
const weeklyPatternsData = useMemo((): any | null => {
  if (!patterns?.daily_patterns) return null;  // ✅ Check daily_patterns

  // daily_patterns has 7 days: {Monday: val, Tuesday: val, ..., Sunday: val}
  const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const weeklyData = weekdays.map(day => patterns.daily_patterns[day] || 0);  // ✅ Extract 7 values

  return {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: `Average Weekly Consumption`,
      data: weeklyData,  // ✅ Array of 7 numbers
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
    }],
  };
}, [patterns?.daily_patterns, selectedMetric]);  // ✅ Depend on daily_patterns
```

### Render condition update:
```typescript
// Line 593: Before
{patterns?.weekly_patterns ? (

// Line 593: After
{weeklyPatternsData ? (  // ✅ Check computed data instead
```

---

## Kết quả

### Before (Incorrect):
```
Average Weekly Consumption
[Chart with 1 column showing ~1.07]
```

### After (Correct):
```
Average Weekly Consumption
[Chart with 7 columns:]
Mon: 540 kWh
Tue: 540 kWh
Wed: 540 kWh
Thu: 540 kWh
Fri: 540 kWh
Sat: 505 kWh  (lower due to weekend ratio)
Sun: 505 kWh  (lower due to weekend ratio)
```

---

## Test Example

### Building: Bear_assembly_Angel (January 2017)

**Backend data**:
- Mean consumption: 540.0 kWh
- Weekday/weekend ratio: 1.07
- Statistics count: 721 readings

**Expected chart display**:
- **Monday-Friday**: 540 kWh (5 tall bars)
- **Saturday-Sunday**: 504.7 kWh (2 shorter bars)
- Pattern: Clear weekday vs weekend difference

---

## Files Modified

**File**: `frontend/src/pages/Analytics.tsx`

**Changes**:
1. Lines 320-337: Updated `weeklyPatternsData` useMemo
   - Changed data source from `patterns.weekly_patterns` to `patterns.daily_patterns`
   - Extract 7 values using `weekdays.map()`
   - Updated dependency array

2. Line 593: Updated render condition
   - Changed from `patterns?.weekly_patterns` to `weeklyPatternsData`

---

## Technical Notes

### Why daily_patterns for weekly chart?

The naming is confusing but correct:
- `daily_patterns`: Contains **per-day-of-week** values (Monday, Tuesday, etc.)
- `weekly_patterns`: Contains **metadata** about weekly patterns (highest day, ratio, etc.)

For visualizing 7 bars representing days of the week, we need the per-day values from `daily_patterns`.

### Data estimation logic

Remember from `analysisApi.ts` transformation:
```typescript
// Weekday consumption = mean
daily_patterns[weekday] = avgValue;  // 540.0

// Weekend consumption = mean / ratio
daily_patterns[weekend] = avgValue / weekdayRatio;  // 540.0 / 1.07 = 504.7
```

This estimation is based on the weekday/weekend ratio provided by backend.

---

## Deployment

```bash
# Copy updated file
docker cp src/pages/Analytics.tsx eaio-frontend:/app/src/pages/Analytics.tsx

# Webpack dev server auto-recompiles (no restart needed)
# Check compilation
docker logs eaio-frontend 2>&1 | tail -20 | grep "Compiled"
# Output: "Compiled with warnings." (OK)
```

---

## Verification

### Step 1: Refresh browser
Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

### Step 2: Navigate to Analytics
URL: http://localhost:3002/analytics

### Step 3: Select building
- Building: Bear_assembly_Angel, Hog_office_Myles, or any with data
- Date Range: 2017-01-01 to 2017-01-31

### Step 4: Scroll to "Average Weekly Consumption"
Should see:
- ✅ 7 vertical bars (one for each day)
- ✅ Weekday bars taller than weekend bars
- ✅ Tooltip on hover shows day name and kWh value

---

**Status**: ✅ Fixed and deployed
**Date**: 2025-12-09
**Impact**: Weekly consumption visualization now shows complete 7-day pattern
