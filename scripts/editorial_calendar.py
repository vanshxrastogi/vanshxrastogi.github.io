"""Generate a planning queue, not publication promises or keyword-volume claims."""
import csv
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOPICS={
'workflows':[
'Plan an AI short film before generating','Build a six-shot AI storyboard','Keep character wardrobe consistent','Create a reference sheet for one location','Turn a logline into scene beats','Plan an animatic before generation','Organize generated takes and rejection notes','Control screen direction across AI shots','Plan a dialogue scene with limited coverage','Use a continuity log across revisions','Build a visual bible for a short series','Plan an AI documentary reconstruction responsibly','Design a repeatable prompt review process','Choose a manageable first-film scope','Review an AI scene without sound','Create alternate cuts from one sequence','Prepare a client review checklist','Archive a completed AI production'],
'camera':[
'Write camera prompts with a clear intention','Wide shot versus wide-angle lens','Dolly movement versus zoom','Low-angle framing without distortion','Plan an over-the-shoulder conversation','Use an arc shot for a product reveal','Choose a useful opening composition','Design a close-up that reveals information','Keep eyelines consistent','Plan motivated camera movement','Use negative space deliberately','Compare eye-level and high-angle views','Create transitions using matching compositions','Plan a reveal without camera confusion','Use depth cues in generated environments','Design a locked-off shot','Plan portrait versus landscape framing','Create a camera-language reference board'],
'postproduction':[
'AI film delivery and backup checklist','Check AI voiceover pronunciation','Balance dialogue against background music','Build ambience across scene cuts','Review generated hands and faces in an edit','Create subtitles that remain readable','Choose master versus web delivery copies','Test uploaded video seeking and playback','Keep version names understandable','Match exposure before creative grading','Review skin tones across generated shots','Use silence to support a scene','Plan sound effects before the final edit','Check lip sync without hiding errors','Compare upscaling on a short test','Protect original frames during export','Create a final viewing checklist','Hand over source and licensed assets'],
'tools':[
'Compare AI video tools with the same test brief','Build a cost-per-usable-shot worksheet','Choose image-to-video versus text-to-video','Evaluate a free plan before production','Read AI tool commercial-use terms','Compare controls rather than demo reels','Track model versions during testing','Evaluate reference-image support','Check whether a tool fits dialogue scenes','Measure generation latency fairly','Review export options before subscribing','Compare motion control on a fixed scene','Document a repeatable tool benchmark','Evaluate video upscaling without invented detail','Decide when local workflows are appropriate','Compare voice tools on pronunciation','Check music-generation editing controls','Maintain a dated tool comparison'],
'commercial':[
'Write an AI product-film brief','Plan a mattress product story without invented claims','Build a property-film shot list','Preserve a product label across AI shots','Plan a concept ad disclosure','Create a brand approval checklist','Translate a product benefit into a scene','Write an AI UGC brief without fake testimonials','Prepare horizontal and vertical ad versions','Plan a CGI product turntable','Build a visual moodboard for a brand','Estimate production effort without a fake price list','Separate concept work from commissioned work','Review advertising claims before delivery','Plan a call to action that fits the film','Handle client revisions with version control','Build a portfolio case study from verified work','Package a campaign cutdown set']}
SOURCES={
'workflows':'https://www.studiobinder.com/blog/ultimate-guide-to-camera-shots/',
'camera':'https://www.studiobinder.com/blog/types-of-camera-shot-angles-in-film/',
'postproduction':'https://www.blackmagicdesign.com/products/davinciresolve',
'tools':'https://runway.com/ | https://higgsfield.ai/ | https://elevenlabs.io/',
'commercial':'https://developers.google.com/search/docs/fundamentals/creating-helpful-content/'}
def main():
    folder=ROOT/'docs/editorial'; folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i in range(18):
        for cat,titles in TOPICS.items():
            n=len(rows)+1; title=titles[i]
            rows.append({'day':n,'suggested_date':str(date(2026,10,20)+timedelta(days=n-1)),'category':cat,'working_title':title,'target_query':title.lower(),'intent':'comparison / decision' if cat=='tools' else 'practical how-to','priority':'P1' if n<=30 else 'P2','status':'research candidate; demand not quantified','source_starting_points':SOURCES[cat]})
    with (folder/'90-day-calendar.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    text=['# First 30 editorial briefs','Planning hypotheses, not measured search demand. Validate each against Search Console once data exists; check current primary sources before drafting. Dates are a queue, not a publishing promise. No keyword volumes, CPC or difficulty scores are invented.']
    for row in rows[:30]:
        title=row['working_title']; cat=row['category']; related=[x for x in rows[:30] if x['category']==cat and x['day']!=row['day']][:2]
        text += [f"\n## {row['day']}. {title}",f"Target query: {row['target_query']}\nIntent: {row['intent']}\nCategory: {cat}",f"Reader value: make a concrete decision about {title[0].lower()+title[1:]}; finish with a reusable checklist rather than a generic tool roundup.",f"Outline: define the production problem; show one labelled example; compare alternatives; list failure signs; give a review checklist.",f"Required evidence: {'run the same brief in the named current tool versions; record plan, settings, cost and rejected takes' if cat=='tools' else 'create a labelled original planning example and check relevant primary documentation; do not claim an unperformed production test'}.",f"Sources to investigate: {row['source_starting_points']}",f"Internal links: /blog/category/{cat}/; "+'; '.join(x['working_title'] for x in related),"Publish gate: facts checked, rights checked, owner reviewed, unique reader value demonstrated. Defer if evidence is insufficient."]
    (folder/'30-article-briefs.md').write_text('\n\n'.join(text),encoding='utf-8')
if __name__=='__main__':main()
