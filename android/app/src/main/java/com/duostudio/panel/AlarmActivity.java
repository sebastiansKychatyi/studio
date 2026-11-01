package com.duostudio.panel;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.AlarmClock;
import android.widget.Toast;

import java.util.ArrayList;

/**
 * Opens the system Clock app with a new alarm, from a panel link:
 * duostudio://alarm?hour=7&minutes=30&label=Wake%20up&days=1,2,3 (JS weekdays, 0 = Sunday).
 * The Clock app shows the alarm, so the user sees it was created.
 */
public class AlarmActivity extends Activity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        try {
            Uri uri = getIntent().getData();
            Intent alarm = new Intent(AlarmClock.ACTION_SET_ALARM)
                    .putExtra(AlarmClock.EXTRA_HOUR, Integer.parseInt(uri.getQueryParameter("hour")))
                    .putExtra(AlarmClock.EXTRA_MINUTES, Integer.parseInt(uri.getQueryParameter("minutes")))
                    .putExtra(AlarmClock.EXTRA_SKIP_UI, false);
            String label = uri.getQueryParameter("label");
            if (label != null && !label.isEmpty()) alarm.putExtra(AlarmClock.EXTRA_MESSAGE, label);
            String days = uri.getQueryParameter("days");
            if (days != null && !days.isEmpty()) {
                // java.util.Calendar: SUNDAY = 1 … SATURDAY = 7
                ArrayList<Integer> list = new ArrayList<>();
                for (String d : days.split(",")) list.add(Integer.parseInt(d.trim()) + 1);
                alarm.putExtra(AlarmClock.EXTRA_DAYS, list);
            }
            startActivity(alarm);
        } catch (Exception e) {
            Toast.makeText(this, R.string.alarmFailed, Toast.LENGTH_LONG).show();
        }
        finish();
    }
}
