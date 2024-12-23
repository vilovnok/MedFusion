import { Injectable } from '@angular/core';
import { HttpClient, HttpRequest, HttpResponse } from '@angular/common/http';
import { concat, concatMap, Observable, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private address = environment.API_BASE_URL;
  constructor(private http: HttpClient) { }

  getResponse(message: string): Observable<string> {
    return this.http.post<string>(this.address, { message });
  }

  handle_get_requests(userObject: any, endpoint: string) {
    return this.http.get<any>(`${this.address}/${endpoint}/${userObject}`)
  }
  handle_post_requests(userObject: any, endpoint: string) {
    console.log(`${this.address}/${endpoint}`);
    return this.http.post<any>(`${this.address}/${endpoint}`, userObject)
  }

  saveToLS(title: string, value: string) {
    return localStorage.setItem(title, value);
  }
  getFromLS(title: string) {
    return localStorage.getItem(title) || "";
  }
  rmFromLS(title: string): void {
    localStorage.removeItem(title);
  }
}
