/*
1.1. TRIGGER - potvrda isporuke, menjanje statusa isporuke, vozaca i vozila
*/

CREATE OR REPLACE TRIGGER trg_isporuka_status
AFTER UPDATE OF status ON isporuka
FOR EACH ROW
BEGIN
    IF :OLD.status <> 'aktivna' AND :NEW.status = 'u_toku' THEN
        UPDATE vozac
        SET status = 'zauzet',
            br_voznji = br_voznji + 1
        WHERE sifra_vo = :NEW.vozac_id;

        UPDATE vozilo
        SET status = 'zauzeto'
        WHERE sifra_v = :NEW.vozilo_id;
    END IF;

    IF :OLD.status <> 'u_toku' AND :NEW.status = 'zavrsena' THEN
        UPDATE vozac
        SET status = 'slobodan'
        WHERE sifra_vo = :NEW.vozac_id;

        UPDATE vozilo
        SET status = 'slobodno'
        WHERE sifra_v = :NEW.vozilo_id;
    END IF;
END;
/

/*
1.2. TRIGGER - automatsko proveravanje datuma registracije vozila prilikom update-a
*/
CREATE OR REPLACE TRIGGER trg_provera_registracije
BEFORE UPDATE OF registracija ON vozilo
FOR EACH ROW
BEGIN
    IF :NEW.registracija < SYSDATE THEN
        :NEW.registracija := ADD_MONTHS(:NEW.registracija, 12);
        IF :NEW.registracija < SYSDATE THEN
            :NEW.registracija := ADD_MONTHS(SYSDATE, 12);
        END IF;
    END IF;
END;
/
--test
SELECT sifra_v, registracija
FROM vozilo
WHERE sifra_v = 241;

UPDATE vozilo
SET registracija = DATE '2022-01-01'
WHERE sifra_v = 241;


/*
 - FUNKCIJA za proveru registracije vozila
*/
CREATE OR REPLACE PROCEDURE proveri_sve_registracije
IS
    CURSOR c_vozila IS
        SELECT sifra_v, marka, model, registracija, status
        FROM vozilo
        WHERE registracija IS NOT NULL;
    
    v_dana_do_isteka NUMBER;
    v_obavestenje_tekst VARCHAR2(500);
BEGIN
    FOR v_vozilo IN c_vozila LOOP
        v_dana_do_isteka := v_vozilo.registracija - SYSDATE;
        
        IF v_dana_do_isteka < 0 AND v_vozilo.status != 'na_servisu' THEN
            
            UPDATE vozilo
            SET status = 'na_servisu'
            WHERE sifra_v = v_vozilo.sifra_v;
            
            DBMS_OUTPUT.PUT_LINE('Vozilo ID: ' || v_vozilo.sifra_v || ' poslato na servis zbog isteka registracije.');
            
        ELSIF v_dana_do_isteka BETWEEN 0 AND 7 THEN
            v_obavestenje_tekst := 'Registracija vozila ' || v_vozilo.sifra_v || 
                                   ' ističe za ' || ROUND(v_dana_do_isteka) || ' dana.';
            
            -- Kreiraj notifikaciju
             FOR admin IN (SELECT sifra_k FROM korisnik WHERE tip_k = 'administrator') 
                LOOP
                    INSERT INTO notifikacija (
                        poruka_n, 
                        datum_n, 
                        procitana_n, 
                        link_n, 
                        korisnik_id
                    ) VALUES (
                        'Registracija vozila ID: '  || :NEW.sifra_v || ', ' || :NEW.marka || ' ' || :NEW.model || 
                        ' ističe za ' || v_razlja_dana || ' dana.',
                        SYSTIMESTAMP,
                        0,
                        '/vozila/' || :NEW.sifra_v,
                        admin.sifra_k
                    );
                END LOOP;
            
            DBMS_OUTPUT.PUT_LINE(v_obavestenje_tekst);
        END IF;
    END LOOP;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Greška u proveri registracija: ' || SQLERRM);
        ROLLBACK;
        RAISE;
END proveri_sve_registracije;
/

-- Zakazivanje dnevne provere pomoću DBMS_SCHEDULER
BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
        job_name        => 'dnevna_provera_registracija_job',
        job_type        => 'PLSQL_BLOCK',
        job_action      => 'BEGIN proveri_sve_registracije; END;',
        start_date      => SYSTIMESTAMP,
        repeat_interval => 'FREQ=DAILY; BYHOUR=8; BYMINUTE=0; BYSECOND=0',
        enabled         => TRUE,
        comments        => 'Dnevna provera isteka registracije vozila'
    );
END;
/


/*
2. PL/SQL FUNKCIJA - izračunavanje ukupnog troška isporuke (gorivo + amortizacija)
*/
CREATE OR REPLACE FUNCTION izracunaj_trosak_isporuke(
    p_isporuka_id IN NUMBER
) RETURN NUMBER
IS
    v_duzina_km NUMBER;
    v_kapacitet NUMBER;
    v_cena_goriva_l NUMBER := 180;
    v_potrosnja_100km NUMBER := 25;
    v_trosak_goriva NUMBER;
    v_trosak_amortizacije NUMBER;
    v_ukupno NUMBER;
BEGIN
    SELECT r.duzina_km, v.kapacitet
    INTO v_duzina_km, v_kapacitet
    FROM isporuka i
    JOIN ruta r ON i.ruta_id = r.sifra_r
    JOIN vozilo v ON i.vozilo_id = v.sifra_v
    WHERE i.sifra_i = p_isporuka_id;
    
    v_trosak_goriva := (v_duzina_km / 100) * v_potrosnja_100km * v_cena_goriva_l;
    
    v_trosak_amortizacije := v_duzina_km * v_kapacitet * 0.001;
    
    v_ukupno := v_trosak_goriva + v_trosak_amortizacije;
    
    RETURN ROUND(v_ukupno, 2);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
    WHEN OTHERS THEN
        RETURN NULL;
END;
/

-- test
SELECT i.sifra_i, i.status, izracunaj_trosak_isporuke(i.sifra_i) as trosak_isporuke
FROM isporuka i
WHERE i.status = 'zavrsena';

BEGIN
    DBMS_OUTPUT.PUT_LINE(izracunaj_trosak_isporuke(21));
END;
/

/*
 3. INDEKSI
*/
-- Kreiranje testnih podataka za demonstraciju performansi
DECLARE
    i NUMBER;
BEGIN
    -- Generiši 10000 testnih isporuka
    FOR i IN 1..10000 LOOP
        INSERT INTO isporuka (ruta_id, vozilo_id, vozac_id, kolicina_kg, status, datum_kreiranja)
        VALUES (
            MOD(i, 100) + 1,
            MOD(i, 50) + 1,
            MOD(i, 30) + 1,
            DBMS_RANDOM.VALUE(100, 5000),
            CASE MOD(i, 4) 
                WHEN 0 THEN 'aktivna'
                WHEN 1 THEN 'u_toku'
                WHEN 2 THEN 'spremna'
                ELSE 'zavrsena'
            END,
            SYSDATE - DBMS_RANDOM.VALUE(0, 365)
        );
    END LOOP;
    COMMIT;
END;
/

-- Kreiranje indeksa za ubrzavanje upita
-- 1. Indeks za često korišćene upite po statusu
CREATE INDEX idx_isporuka_status ON isporuka(status);

-- 2. Kompozitni indeks za upite koji filtriraju vozila po kapacitetu i statusu
CREATE INDEX idx_vozilo_kapacitet_status ON vozilo(kapacitet, status);

-- 3. Indeks za upite koji spajaju tabele
-- CREATE INDEX idx_ruta_polazna_odrediste ON ruta(polazna_tacka, odrediste);

-- 4. Indeks za upite sa LIKE pretragom
-- CREATE INDEX idx_korisnik_ime_prz ON korisnik(ime_k, prz_k);

-- Demonstracija razlike u performansama
-- UPIT BEZ INDEKSA (pretpostavimo da obrišemo indekse prvo)
EXPLAIN PLAN FOR
SELECT i.*, r.polazna_tacka, r.odrediste
FROM isporuka i
JOIN ruta r ON i.ruta_id = r.sifra_r
WHERE i.status = 'u_toku'
AND i.datum_kreiranja > SYSDATE - 30;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- Nakon kreiranja indeksa, isti upit će biti brži


/*
 4. IZVEŠTAJ - o isporukama po vozilu i vozaču za period u prethodnih mesec dana
*/

CREATE OR REPLACE TYPE t_isporuka_info AS OBJECT (
    vozilo_id NUMBER,
    vozac_id NUMBER,
    broj_isporuka NUMBER,
    ukupna_kolicina NUMBER,
    ukupni_trosak NUMBER
);
/

CREATE OR REPLACE TYPE t_isporuka_tab AS TABLE OF t_isporuka_info;
/

CREATE OR REPLACE FUNCTION izvestaj_isporuka_30_dana
RETURN t_isporuka_tab
PIPELINED
IS
    CURSOR c_izvestaj IS
        WITH osnovni_podaci AS (
            SELECT
                i.vozilo_id,
                v.marka || ' ' || v.model AS vozilo,
                i.vozac_id,
                vo.ime_vo || ' ' || vo.prz_vo AS vozac,
                COUNT(*) AS broj_isporuka,
                SUM(i.kolicina_kg) AS ukupna_kolicina,
                SUM(izracunaj_trosak_isporuke(i.sifra_i)) AS ukupni_trosak
            FROM isporuka i
            JOIN vozilo v ON i.vozilo_id = v.sifra_v
            JOIN vozac vo ON i.vozac_id = vo.sifra_vo
            WHERE i.datum_kreiranja >= SYSDATE - 30
            GROUP BY i.vozilo_id, v.marka, v.model, i.vozac_id, vo.ime_vo, vo.prz_vo
            HAVING COUNT(*) > 0
        )
        SELECT * FROM osnovni_podaci;
BEGIN
    FOR r IN c_izvestaj LOOP
        PIPE ROW(
            t_isporuka_info(
                r.vozilo_id,
                r.vozac_id,
                r.broj_isporuka,
                r.ukupna_kolicina,
                r.ukupni_trosak
            )
        );
    END LOOP;
    RETURN;
END;
/

-- Test funkcije za izveštaj
SELECT *
FROM TABLE(izvestaj_isporuka_30_dana);

