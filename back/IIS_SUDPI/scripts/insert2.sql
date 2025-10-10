DELETE FROM KORISNIK;
DELETE FROM LOGISTICKI_KOORDINATOR;
DELETE FROM SKLADISNI_OPERATER;
DELETE FROM NABAVNI_MENADZER;
DELETE FROM FINANSIJSKI_ANALITICAR;
DELETE FROM KONTROLOR_KVALITETA;
DELETE FROM ADMINISTRATOR;
DELETE FROM REKLAMACIJA;
DELETE FROM POSETA;
DELETE FROM SERTIFIKAT;
DELETE FROM DOBAVLJAC;

COMMIT;

-- USERS -- password for all users is 'asdf1234'
-- user: admin@gmail.com
-- user: fa@gmail.com
-- user: nm@gmail.com
-- user: kk@gmail.com
-- user: so@gmail.com
-- user: lk@gmail.com

INSERT INTO KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$B3xR7ru7zpmuld5qdzIpqC$BsV3vuNoa+jF9zeJI6dAsFGyCvb9gfo7wKVZ1NtU06s=',null,0,'admin@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.47.28.960782000 PM','DD-MON-RR HH.MI.SSXFF AM'),1,'admin','admin','admin@gmail.com','administrator');
INSERT INTO KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$Fs66hQbo0aNq4RRk0jDr7G$/IqDyqwzz5xvl4UKKw6i017cAdSN2xYzRPysZ/eqsIQ=',null,0,'fa@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.47.54.013286000 PM','DD-MON-RR HH.MI.SSXFF AM'),2,'fa','fa','fa@gmail.com','finansijski_analiticar');
INSERT INTO KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$fAO2m0Cz8Tq8mcHM4aDvjZ$X9CbeztmdKPRYrv5o0iJxAIagaWq7vuXq4Mp1WkaxpQ=',null,0,'nm@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.48.06.375977000 PM','DD-MON-RR HH.MI.SSXFF AM'),3,'nm','nm','nm@gmail.com','nabavni_menadzer');
INSERT INTO KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$Ak4c4lNfzUPEvtURtnpRcY$HObZg0hIVJBfVu5Kr2SRNLWIvtGFRstAAOhFkeCTzNE=',null,0,'kk@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.48.24.992730000 PM','DD-MON-RR HH.MI.SSXFF AM'),4,'kk','kk','kk@gmail.com','kontrolor_kvaliteta');
INSERT INTO KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$8qdZ57YzsnWq5GEGYMacwq$cNPKV4mHgyhJSsnaE3xPNiNGtW49y9j3wqOwK83MSUQ=',null,0,'so@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.48.58.099532000 PM','DD-MON-RR HH.MI.SSXFF AM'),5,'so','so','so@gmail.com','skladisni_operater');
INSERT INTO KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$73qKNuQE9hQk4bwxlStUmZ$SpJxoVY0PAaE64kKYsa344M/uZh2zWT1Myb4t+3EqN8=',null,0,'lk@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.49.12.522763000 PM','DD-MON-RR HH.MI.SSXFF AM'),6,'lk','lk','lk@gmail.com','logisticki_koordinator');
INSERT INTO ADMINISTRATOR (ID,KORISNIK_ID) values (1,1);
INSERT INTO FINANSIJSKI_ANALITICAR (ID,KORISNIK_ID) values (1,2);
INSERT INTO NABAVNI_MENADZER (ID,KORISNIK_ID) values (1,3);
INSERT INTO KONTROLOR_KVALITETA (ID,KORISNIK_ID) values (1,4);
INSERT INTO SKLADISNI_OPERATER (ID,KORISNIK_ID) values (1,5);
INSERT INTO LOGISTICKI_KOORDINATOR (ID,KORISNIK_ID) values (1,6);
COMMIT;

-- Insert DOBAVLJAC records with properly named materials using CASE statement
BEGIN
  FOR i IN 1..50 LOOP
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
      CASE MOD(i, 8)
        WHEN 0 THEN 'Cimet'
        WHEN 1 THEN 'Mleko'
        WHEN 2 THEN 'Biber'
        WHEN 3 THEN 'Kakao'
        WHEN 4 THEN 'Ulje'
        WHEN 5 THEN 'So'
        WHEN 6 THEN 'Med'
        WHEN 7 THEN 'Secer'
      END,
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

BEGIN
  INSERT INTO REKLAMACIJA (
    REKLAMACIJA_ID,
    DATUM_PRIJEMA,
    STATUS,
    OPIS_PROBLEMA,
    VREME_TRAJANJA,
    JACINA_ZALBE,
    KONTROLOR_ID,
    DOBAVLJAC_ID
  ) VALUES (
    1,
    TRUNC(SYSDATE - 15),
    'prijem',
    'Loš kvalitet isporučene sirovine, ne odgovara specifikacijama',
    7,
    8,
    1,
    1
  );
  
  INSERT INTO REKLAMACIJA (
    REKLAMACIJA_ID,
    DATUM_PRIJEMA,
    STATUS,
    OPIS_PROBLEMA,
    VREME_TRAJANJA,
    JACINA_ZALBE,
    KONTROLOR_ID,
    DOBAVLJAC_ID
  ) VALUES (
    2,
    TRUNC(SYSDATE - 10),
    'analiza',
    'Kašnjenje u isporuci više od ugovorenog roka',
    5,
    6,
    1,
    1
  );
  
  INSERT INTO REKLAMACIJA (
    REKLAMACIJA_ID,
    DATUM_PRIJEMA,
    STATUS,
    OPIS_PROBLEMA,
    VREME_TRAJANJA,
    JACINA_ZALBE,
    KONTROLOR_ID,
    DOBAVLJAC_ID
  ) VALUES (
    3,
    TRUNC(SYSDATE - 5),
    'odgovor',
    'Neusklađenost isporučene količine sa narudžbinom',
    3,
    7,
    1,
    1
  );
  
  -- Insert additional random REKLAMACIJA records for other suppliers
  FOR i IN 4..30 LOOP
    INSERT INTO REKLAMACIJA (
      REKLAMACIJA_ID,
      DATUM_PRIJEMA,
      STATUS,
      OPIS_PROBLEMA,
      VREME_TRAJANJA,
      JACINA_ZALBE,
      KONTROLOR_ID,
      DOBAVLJAC_ID
    ) VALUES (
      i,
      TRUNC(SYSDATE - DBMS_RANDOM.VALUE(1, 60)),
      CASE MOD(i, 4)
        WHEN 0 THEN 'prijem'
        WHEN 1 THEN 'analiza'
        WHEN 2 THEN 'odgovor'
        ELSE 'zatvaranje'
      END,
      CASE MOD(i, 5)
        WHEN 0 THEN 'Oštećena ambalaža tokom transporta'
        WHEN 1 THEN 'Neusaglašenost kvaliteta sa dokumentacijom'
        WHEN 2 THEN 'Kašnjenje isporuke više od dozvoljenog roka'
        WHEN 3 THEN 'Nekompletna dokumentacija o poreklu sirovine'
        ELSE 'Pogrešno isporučena količina'
      END,
      TRUNC(DBMS_RANDOM.VALUE(1, 14)),
      TRUNC(DBMS_RANDOM.VALUE(1, 10)),
      1,
      TRUNC(DBMS_RANDOM.VALUE(2, 50))
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
