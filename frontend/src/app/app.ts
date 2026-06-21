import { JsonPipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [
    JsonPipe
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  /**
   * Provides the HttpClient service for making HTTP requests.
   */
  private http = inject(HttpClient);

  /**
   * Data coming from the API
   */
  apiData = signal<any>(null);

  /**
   * Initializes the component.
   */
  ngOnInit(): void {
    this.loadData();
  }

  loadData() {
    this.http.get('http://127.0.0.1:8000/max/track/Spa/fastest-lap')
      .subscribe({
        next: (response) => {
          this.apiData.set(response);
        },
        error: (err) => {
          console.log(err);
        }
      });
  }
}
