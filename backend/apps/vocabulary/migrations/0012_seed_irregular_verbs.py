from django.db import migrations

# (infinitive, transcription, past, transcription, participle, transcription, translation)
# Where British and American spelling differ, both are given: either one counts.
VERBS = [
    ('be', '[biː]', 'was / were', '[wɒz] / [wɜː]', 'been', '[biːn]', 'быть'),
    ('begin', '[bɪˈɡɪn]', 'began', '[bɪˈɡæn]', 'begun', '[bɪˈɡʌn]', 'начинать'),
    ('blow', '[bləʊ]', 'blew', '[bluː]', 'blown', '[bləʊn]', 'дуть'),
    ('break', '[breɪk]', 'broke', '[brəʊk]', 'broken', '[ˈbrəʊk(ə)n]', 'ломать'),
    ('bring', '[brɪŋ]', 'brought', '[brɔːt]', 'brought', '[brɔːt]', 'приносить'),
    ('build', '[bɪld]', 'built', '[bɪlt]', 'built', '[bɪlt]', 'строить'),
    ('buy', '[baɪ]', 'bought', '[bɔːt]', 'bought', '[bɔːt]', 'покупать'),
    ('catch', '[kætʃ]', 'caught', '[kɔːt]', 'caught', '[kɔːt]', 'ловить'),
    ('choose', '[tʃuːz]', 'chose', '[tʃəʊz]', 'chosen', '[ˈtʃəʊz(ə)n]', 'выбирать'),
    ('come', '[kʌm]', 'came', '[keɪm]', 'come', '[kʌm]', 'приходить'),
    ('cost', '[kɒst]', 'cost', '[kɒst]', 'cost', '[kɒst]', 'стоить'),
    ('cut', '[kʌt]', 'cut', '[kʌt]', 'cut', '[kʌt]', 'резать'),
    ('do', '[duː]', 'did', '[dɪd]', 'done', '[dʌn]', 'делать'),
    ('draw', '[drɔː]', 'drew', '[druː]', 'drawn', '[drɔːn]', 'чертить, рисовать'),
    ('dream', '[driːm]', 'dreamt / dreamed', '[dremt]', 'dreamt / dreamed', '[dremt]', 'мечтать'),
    ('drink', '[drɪŋk]', 'drank', '[dræŋk]', 'drunk', '[drʌŋk]', 'пить'),
    ('drive', '[draɪv]', 'drove', '[drəʊv]', 'driven', '[ˈdrɪv(ə)n]', 'водить'),
    ('eat', '[iːt]', 'ate', '[eɪt]', 'eaten', '[ˈiːt(ə)n]', 'есть'),
    ('fall', '[fɔːl]', 'fell', '[fel]', 'fallen', '[ˈfɔːlən]', 'падать'),
    ('feel', '[fiːl]', 'felt', '[felt]', 'felt', '[felt]', 'чувствовать'),
    ('find', '[faɪnd]', 'found', '[faʊnd]', 'found', '[faʊnd]', 'находить'),
    ('fly', '[flaɪ]', 'flew', '[fluː]', 'flown', '[fləʊn]', 'летать'),
    ('forget', '[fəˈɡet]', 'forgot', '[fəˈɡɒt]', 'forgotten', '[fəˈɡɒt(ə)n]', 'забывать'),
    ('get', '[ɡet]', 'got', '[ɡɒt]', 'got', '[ɡɒt]', 'получать'),
    ('give', '[ɡɪv]', 'gave', '[ɡeɪv]', 'given', '[ˈɡɪv(ə)n]', 'давать'),
    ('go', '[ɡəʊ]', 'went', '[went]', 'gone', '[ɡɒn]', 'идти'),
    ('grow', '[ɡrəʊ]', 'grew', '[ɡruː]', 'grown', '[ɡrəʊn]', 'расти'),
    ('have', '[hæv]', 'had', '[hæd]', 'had', '[hæd]', 'иметь'),
    ('hear', '[hɪə]', 'heard', '[hɜːd]', 'heard', '[hɜːd]', 'слышать'),
    ('hide', '[haɪd]', 'hid', '[hɪd]', 'hidden', '[ˈhɪd(ə)n]', 'прятать'),
    ('hold', '[həʊld]', 'held', '[held]', 'held', '[held]', 'держать'),
    ('hurt', '[hɜːt]', 'hurt', '[hɜːt]', 'hurt', '[hɜːt]', 'ранить'),
    ('keep', '[kiːp]', 'kept', '[kept]', 'kept', '[kept]', 'хранить, держать'),
    ('know', '[nəʊ]', 'knew', '[njuː]', 'known', '[nəʊn]', 'знать'),
    ('lay', '[leɪ]', 'laid', '[leɪd]', 'laid', '[leɪd]', 'положить'),
    ('learn', '[lɜːn]', 'learnt / learned', '[lɜːnt]', 'learnt / learned', '[lɜːnt]', 'учить'),
    ('leave', '[liːv]', 'left', '[left]', 'left', '[left]', 'покидать'),
    ('let', '[let]', 'let', '[let]', 'let', '[let]', 'позволять'),
    ('light', '[laɪt]', 'lit', '[lɪt]', 'lit', '[lɪt]', 'освещать'),
    ('lose', '[luːz]', 'lost', '[lɒst]', 'lost', '[lɒst]', 'терять'),
    ('make', '[meɪk]', 'made', '[meɪd]', 'made', '[meɪd]', 'изготавливать'),
    ('mean', '[miːn]', 'meant', '[ment]', 'meant', '[ment]', 'иметь в виду'),
    ('meet', '[miːt]', 'met', '[met]', 'met', '[met]', 'встречать'),
    ('pay', '[peɪ]', 'paid', '[peɪd]', 'paid', '[peɪd]', 'платить'),
    ('put', '[pʊt]', 'put', '[pʊt]', 'put', '[pʊt]', 'класть'),
    ('read', '[riːd]', 'read', '[red]', 'read', '[red]', 'читать'),
    ('ride', '[raɪd]', 'rode', '[rəʊd]', 'ridden', '[ˈrɪd(ə)n]', 'ехать верхом'),
    ('ring', '[rɪŋ]', 'rang', '[ræŋ]', 'rung', '[rʌŋ]', 'звенеть'),
    ('rise', '[raɪz]', 'rose', '[rəʊz]', 'risen', '[ˈrɪz(ə)n]', 'подниматься'),
    ('run', '[rʌn]', 'ran', '[ræn]', 'run', '[rʌn]', 'бежать'),
    ('say', '[seɪ]', 'said', '[sed]', 'said', '[sed]', 'сказать'),
    ('see', '[siː]', 'saw', '[sɔː]', 'seen', '[siːn]', 'видеть'),
    ('sell', '[sel]', 'sold', '[səʊld]', 'sold', '[səʊld]', 'продавать'),
    ('send', '[send]', 'sent', '[sent]', 'sent', '[sent]', 'посылать'),
    ('set', '[set]', 'set', '[set]', 'set', '[set]', 'ставить'),
    ('shake', '[ʃeɪk]', 'shook', '[ʃʊk]', 'shaken', '[ˈʃeɪk(ə)n]', 'трясти'),
    ('shut', '[ʃʌt]', 'shut', '[ʃʌt]', 'shut', '[ʃʌt]', 'закрывать'),
    ('sing', '[sɪŋ]', 'sang', '[sæŋ]', 'sung', '[sʌŋ]', 'петь'),
    ('sit', '[sɪt]', 'sat', '[sæt]', 'sat', '[sæt]', 'сидеть'),
    ('sleep', '[sliːp]', 'slept', '[slept]', 'slept', '[slept]', 'спать'),
    ('speak', '[spiːk]', 'spoke', '[spəʊk]', 'spoken', '[ˈspəʊk(ə)n]', 'говорить'),
    ('spend', '[spend]', 'spent', '[spent]', 'spent', '[spent]', 'тратить'),
    ('stand', '[stænd]', 'stood', '[stʊd]', 'stood', '[stʊd]', 'стоять'),
    ('swim', '[swɪm]', 'swam', '[swæm]', 'swum', '[swʌm]', 'плавать'),
    ('take', '[teɪk]', 'took', '[tʊk]', 'taken', '[ˈteɪk(ə)n]', 'брать'),
    ('teach', '[tiːtʃ]', 'taught', '[tɔːt]', 'taught', '[tɔːt]', 'учить (кого-то)'),
    ('tell', '[tel]', 'told', '[təʊld]', 'told', '[təʊld]', 'рассказывать'),
    ('think', '[θɪŋk]', 'thought', '[θɔːt]', 'thought', '[θɔːt]', 'думать'),
    ('understand', '[ˌʌndəˈstænd]', 'understood', '[ˌʌndəˈstʊd]', 'understood', '[ˌʌndəˈstʊd]', 'понимать'),
    ('wake', '[weɪk]', 'woke', '[wəʊk]', 'woken', '[ˈwəʊk(ə)n]', 'просыпаться'),
    ('wear', '[weə]', 'wore', '[wɔː]', 'worn', '[wɔːn]', 'носить'),
    ('win', '[wɪn]', 'won', '[wʌn]', 'won', '[wʌn]', 'побеждать'),
    ('write', '[raɪt]', 'wrote', '[rəʊt]', 'written', '[ˈrɪt(ə)n]', 'писать'),
]


def seed_verbs(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    IrregularVerb = apps.get_model('vocabulary', 'IrregularVerb')
    language = Language.objects.filter(code='en').first()
    if language is None:
        return
    for infinitive, inf_tr, past, past_tr, participle, part_tr, translation in VERBS:
        IrregularVerb.objects.update_or_create(
            language=language, infinitive=infinitive,
            defaults={
                'infinitive_transcription': inf_tr, 'past': past, 'past_transcription': past_tr,
                'participle': participle, 'participle_transcription': part_tr, 'translation': translation,
            },
        )


def remove_verbs(apps, schema_editor):
    IrregularVerb = apps.get_model('vocabulary', 'IrregularVerb')
    IrregularVerb.objects.filter(language__code='en', infinitive__in=[v[0] for v in VERBS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_english_language'),
        ('vocabulary', '0011_irregularverb'),
    ]

    operations = [
        migrations.RunPython(seed_verbs, remove_verbs),
    ]
