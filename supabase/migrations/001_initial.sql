create extension if not exists pg_trgm;

create table records (
  id                     bigserial primary key,
  record_id              text not null unique,
  transcription          text not null,
  transcription_normalized text not null,
  gloss                  text,
  ort                    text,
  audio_path             text,
  uploaded_at            timestamptz default now()
);

create index idx_transcription_normalized
  on records using gin(transcription_normalized gin_trgm_ops);

alter table records enable row level security;

create policy "authenticated users can read records"
  on records for select
  using (auth.role() = 'authenticated');

create policy "authenticated users can insert records"
  on records for insert
  with check (auth.role() = 'authenticated');
