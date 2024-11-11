import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopicDialogComponent } from './topic-dialog.component';

describe('TopicDialogComponent', () => {
  let component: TopicDialogComponent;
  let fixture: ComponentFixture<TopicDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TopicDialogComponent]
    });
    fixture = TestBed.createComponent(TopicDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
