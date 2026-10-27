package ro.chilipir.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.net.URI;
import java.util.Locale;

public class MainActivity extends Activity {
    LinearLayout root, results;
    EditText url, title, price, reference;
    Spinner category;
    final int ink = Color.rgb(24, 42, 57);
    final int teal = Color.rgb(0, 121, 113);

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll = new ScrollView(this);
        root = new LinearLayout(this); root.setOrientation(1); root.setPadding(28,32,28,32);
        root.setBackgroundColor(Color.rgb(247,249,250)); scroll.addView(root); setContentView(scroll);
        TextView heading = text("CHILIPIR", 29, true); heading.setTextColor(teal); root.addView(heading);
        root.addView(text("Artă & Foto • OLX România", 16, false));
        root.addView(text("Evaluează anunțuri introduse de tine. Căutarea automată OLX nu este încă disponibilă.", 14, false));
        title = field("Titlul anunțului", false);
        url = field("Link OLX (https://www.olx.ro/d/...)", false);
        category = new Spinner(this);
        category.setAdapter(new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, new String[]{"Foto", "Artă"}));
        root.addView(category);
        price = field("Preț cerut (lei)", true);
        reference = field("Preț de referință estimat (lei)", true);
        Button save = new Button(this); save.setText("EVALUEAZĂ ȘI SALVEAZĂ"); save.setTextColor(Color.WHITE); save.setBackgroundTintList(android.content.res.ColorStateList.valueOf(teal));
        root.addView(save); save.setOnClickListener(v -> addListing());
        root.addView(text("Anunțurile mele", 22, true));
        results = new LinearLayout(this); results.setOrientation(1); root.addView(results); render();
    }
    TextView text(String s, int size, boolean bold) {
        TextView t = new TextView(this); t.setText(s); t.setTextSize(size); t.setTextColor(ink);
        t.setPadding(0,12,0,12); if(bold)t.setTypeface(null, Typeface.BOLD); return t;
    }
    EditText field(String hint, boolean numeric) {
        EditText e = new EditText(this); e.setSingleLine(true); e.setHint(hint);
        if(numeric)e.setInputType(android.text.InputType.TYPE_CLASS_NUMBER | android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL);
        root.addView(e); return e;
    }
    boolean validOlx(String link) {
        try {
            URI uri = new URI(link);
            String host = uri.getHost();
            return "https".equalsIgnoreCase(uri.getScheme()) && host != null &&
                (host.equalsIgnoreCase("olx.ro") || host.equalsIgnoreCase("www.olx.ro")) &&
                uri.getPath() != null && uri.getPath().startsWith("/d/") && uri.getUserInfo() == null;
        } catch(Exception ex) { return false; }
    }
    void addListing() {
        String link = url.getText().toString().trim();
        if(!validOlx(link)) { toast("Introdu un link OLX valid, de tip /d/"); return; }
        if(title.getText().toString().trim().isEmpty()) { toast("Introdu titlul"); return; }
        try {
            double p = Double.parseDouble(price.getText().toString().replace(",","."));
            double r = Double.parseDouble(reference.getText().toString().replace(",","."));
            if(!Double.isFinite(p)||!Double.isFinite(r)||p<0||r<=0)throw new Exception();
            JSONObject item = new JSONObject();
            item.put("url",link); item.put("title",title.getText().toString().trim());
            item.put("category",category.getSelectedItem().toString()); item.put("price",p); item.put("reference",r);
            JSONArray data = load(); JSONArray updated = new JSONArray(); updated.put(item);
            for(int i=0;i<data.length();i++)if(!link.equals(data.getJSONObject(i).optString("url")))updated.put(data.getJSONObject(i));
            getPreferences(MODE_PRIVATE).edit().putString("listings",updated.toString()).apply();
            render(); toast("Salvat");
        } catch(Exception ex) { toast("Prețurile trebuie să fie numere valide"); }
    }
    JSONArray load() {
        try { return new JSONArray(getPreferences(MODE_PRIVATE).getString("listings","[]")); }
        catch(Exception ex) { return new JSONArray(); }
    }
    void render() {
        results.removeAllViews(); JSONArray data = load();
        if(data.length()==0) { results.addView(text("Nu ai salvat încă anunțuri.",14,false)); return; }
        for(int i=0;i<data.length();i++) {
            JSONObject o=data.optJSONObject(i); if(o==null)continue;
            String link=o.optString("url"); double p=o.optDouble("price"),r=o.optDouble("reference");
            double discount=Math.max(0,(r-p)/r*100);
            LinearLayout card=new LinearLayout(this); card.setOrientation(1); card.setPadding(16,16,16,16);
            card.setBackgroundColor(Color.WHITE);
            card.addView(text(o.optString("title")+" • "+o.optString("category"),17,true));
            card.addView(text(String.format(Locale.getDefault(),"%.0f lei • reducere estimată %.1f%%",p,discount),15,false));
            card.addView(text("Estimare bazată pe prețul de referință introdus, nu pe vânzări verificate.",12,false));
            Button open=new Button(this); open.setText("DESCHIDE PE OLX"); card.addView(open);
            open.setOnClickListener(v -> startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(link))));
            results.addView(card);
            View spacer=new View(this); results.addView(spacer,new LinearLayout.LayoutParams(1,14));
        }
    }
    void toast(String msg) { Toast.makeText(this,msg,Toast.LENGTH_LONG).show(); }
}
