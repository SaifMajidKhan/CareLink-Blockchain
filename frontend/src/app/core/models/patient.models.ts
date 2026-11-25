export interface Patient {
  id: number;
  name: string;
  age: number;
  condition: string;
  created_at: string;
}

export interface PatientCreate {
  name: string;
  age: number;
  condition: string;
}