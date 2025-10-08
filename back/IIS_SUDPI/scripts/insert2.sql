DELETE FROM REKLAMACIJA;
DELETE FROM DOBAVLJAC;
DELETE FROM SERTIFIKAT;
COMMIT;

BEGIN
  FOR i IN 10..50 LOOP
    INSERT INTO DOBAVLJAC (
      SIFRA_D,
      NAZIV,
      EMAIL,
      PIB_D,
      IME_SIROVINE,
      CENA,
      ROK_ISPORUKE,
      OCENA,
      DATUM_OCENJIVANJA,
      IZABRAN
    ) VALUES (
      i,
      'Dobavljac_' || i,
      'email' || i || '@example.com',
      'PIB' || LPAD(i, 2, '0'),
      'Sirovina_' || i,
      ROUND(DBMS_RANDOM.VALUE(50, 500), 2),
      TRUNC(DBMS_RANDOM.VALUE(1, 30)),
      ROUND(DBMS_RANDOM.VALUE(1, 5), 1),
      TRUNC(SYSDATE - DBMS_RANDOM.VALUE(1, 365)),
      CASE WHEN DBMS_RANDOM.VALUE < 0.5 THEN 0 ELSE 1 END
    );
  END LOOP;
  COMMIT;
END;
/

COMMIT;

-- Generate certificates with fixed values instead of arrays
BEGIN
  -- Critical certificates (expiring in 1-7 days)
  FOR i IN 20..23 LOOP
    INSERT INTO SERTIFIKAT (
      SERTIFIKAT_ID,
      NAZIV,
      TIP,
      DATUM_IZDAVANJA,
      DATUM_ISTEKA,
      DOBAVLJAC_ID
    ) VALUES (
      i,
      CASE MOD(i, 5)
        WHEN 0 THEN 'ISO 9001 Quality Management Certificate'
        WHEN 1 THEN 'HACCP Food Safety Certificate'
        WHEN 2 THEN 'GMP Manufacturing Certificate'
        WHEN 3 THEN 'BRC Global Standard Certificate'
        ELSE 'IFS Food Safety Certificate'
      END,
      CASE MOD(i, 5)
        WHEN 0 THEN 'ISO'
        WHEN 1 THEN 'HACCP'
        WHEN 2 THEN 'GMP'
        WHEN 3 THEN 'BRC'
        ELSE 'IFS'
      END,
      TRUNC(SYSDATE - 330),
      TRUNC(SYSDATE + DBMS_RANDOM.VALUE(1, 7)),
      TRUNC(DBMS_RANDOM.VALUE(10, 50))
    );
  END LOOP;
  
  -- Warning certificates (expiring in 8-14 days)
  FOR i IN 24..26 LOOP
    INSERT INTO SERTIFIKAT (
      SERTIFIKAT_ID,
      NAZIV,
      TIP,
      DATUM_IZDAVANJA,
      DATUM_ISTEKA,
      DOBAVLJAC_ID
    ) VALUES (
      i,
      CASE MOD(i, 5)
        WHEN 0 THEN 'ISO 9001 Quality Management Certificate'
        WHEN 1 THEN 'HACCP Food Safety Certificate'
        WHEN 2 THEN 'GMP Manufacturing Certificate'
        WHEN 3 THEN 'BRC Global Standard Certificate'
        ELSE 'IFS Food Safety Certificate'
      END,
      CASE MOD(i, 5)
        WHEN 0 THEN 'ISO'
        WHEN 1 THEN 'HACCP'
        WHEN 2 THEN 'GMP'
        WHEN 3 THEN 'BRC'
        ELSE 'IFS'
      END,
      TRUNC(SYSDATE - 300),
      TRUNC(SYSDATE + DBMS_RANDOM.VALUE(8, 14)),
      TRUNC(DBMS_RANDOM.VALUE(10, 50))
    );
  END LOOP;
  
  -- Notice certificates (expiring in 15-30 days)
  FOR i IN 27..32 LOOP
    INSERT INTO SERTIFIKAT (
      SERTIFIKAT_ID,
      NAZIV,
      TIP,
      DATUM_IZDAVANJA,
      DATUM_ISTEKA,
      DOBAVLJAC_ID
    ) VALUES (
      i,
      CASE MOD(i, 5)
        WHEN 0 THEN 'ISO 9001 Quality Management Certificate'
        WHEN 1 THEN 'HACCP Food Safety Certificate'
        WHEN 2 THEN 'GMP Manufacturing Certificate'
        WHEN 3 THEN 'BRC Global Standard Certificate'
        ELSE 'IFS Food Safety Certificate'
      END,
      CASE MOD(i, 5)
        WHEN 0 THEN 'ISO'
        WHEN 1 THEN 'HACCP'
        WHEN 2 THEN 'GMP'
        WHEN 3 THEN 'BRC'
        ELSE 'IFS'
      END,
      TRUNC(SYSDATE - 270),
      TRUNC(SYSDATE + DBMS_RANDOM.VALUE(15, 30)),
      TRUNC(DBMS_RANDOM.VALUE(10, 50))
    );
  END LOOP;
  
  COMMIT;
END;
